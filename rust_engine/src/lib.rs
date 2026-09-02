use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict};
use rusqlite::{params, Connection};
use std::ops::Bound::{Excluded, Unbounded};
use std::sync::Mutex;

pub struct FileMetadata {
    pub path: String,
    pub size: u64,
    pub mtime_ns: u64,
    pub entry_dt: String,
    pub digest: Option<Vec<u8>>,
    pub digest_partial: Option<Vec<u8>>,
    pub digest_samples: Option<Vec<u8>>,
}

// Helper to convert FileMetadata to a Python dict
fn file_metadata_to_dict<'py>(py: Python<'py>, meta: &FileMetadata) -> PyResult<Bound<'py, PyDict>> {
    let dict = PyDict::new(py);
    dict.set_item("path", &meta.path)?;
    dict.set_item("size", meta.size)?;
    dict.set_item("mtime_ns", meta.mtime_ns)?;
    dict.set_item("entry_dt", &meta.entry_dt)?;

    if let Some(ref d) = meta.digest {
        dict.set_item("digest", PyBytes::new(py, d))?;
    } else {
        dict.set_item("digest", py.None())?;
    }
    if let Some(ref dp) = meta.digest_partial {
        dict.set_item("digest_partial", PyBytes::new(py, dp))?;
    } else {
        dict.set_item("digest_partial", py.None())?;
    }
    if let Some(ref ds) = meta.digest_samples {
        dict.set_item("digest_samples", PyBytes::new(py, ds))?;
    } else {
        dict.set_item("digest_samples", py.None())?;
    }
    Ok(dict)
}

pub trait CacheEngine {
    fn clear(&self) -> Result<(), String>;
    fn close(&self) -> Result<(), String>;
    fn commit(&self) -> Result<(), String>;
    fn mark_directory_scanned(&self, dir_path: &str) -> Result<(), String>;
    fn is_directory_scanned(&self, dir_path: &str) -> Result<bool, String>;
    fn snapshot_file(&self, path: &str, size: u64, mtime: f64) -> Result<(), String>;
    fn snapshot_files_batch(&self, batch: &[(String, u64, f64)]) -> Result<(), String>;
    fn get_files_in_directory_page(
        &self,
        dir_path: &str,
        last_path: &str,
        limit: usize,
    ) -> Result<Vec<FileMetadata>, String>;
    fn get_candidate_sizes(&self) -> Result<Vec<u64>, String>;
    fn get_files_by_sizes_page(
        &self,
        sizes: &[u64],
        last_path: &str,
        limit: usize,
    ) -> Result<Vec<FileMetadata>, String>;
    fn get(
        &self,
        path: &str,
        key: &str,
        size: u64,
        mtime_ns: u64,
        ignore_mtime: bool,
    ) -> Result<Option<Vec<u8>>, String>;
    fn put(&self, path: &str, size: u64, mtime_ns: u64, key: &str, value: &[u8]) -> Result<(), String>;
    fn get_cache_viewer_files(
        &self,
        search: Option<&str>,
        limit: usize,
        offset: usize,
    ) -> Result<(usize, Vec<FileMetadata>), String>;
}

// ==========================================
// SQLite Cache Engine Implementation
// ==========================================

pub struct RustSQLiteCacheEngine {
    conn: Mutex<Connection>,
}

impl RustSQLiteCacheEngine {
    pub fn new(path: &str) -> Result<Self, String> {
        let conn = Connection::open(path).map_err(|e| e.to_string())?;
        let _ = conn.execute("PRAGMA busy_timeout = 30000;", []);
        let _ = conn.busy_timeout(std::time::Duration::from_secs(30));
        // Enable WAL mode for high concurrency
        let _ = conn.execute("PRAGMA journal_mode=WAL;", []);

        conn.execute(
            "CREATE TABLE IF NOT EXISTS files (
                path TEXT PRIMARY KEY,
                size INTEGER,
                mtime_ns INTEGER,
                entry_dt DATETIME,
                digest BLOB,
                digest_partial BLOB,
                digest_samples BLOB
            )",
            [],
        )
        .map_err(|e| e.to_string())?;

        conn.execute(
            "CREATE TABLE IF NOT EXISTS scanned_directories (
                path TEXT PRIMARY KEY,
                scan_dt DATETIME
            )",
            [],
        )
        .map_err(|e| e.to_string())?;

        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_files_size ON files (size)",
            [],
        )
        .map_err(|e| e.to_string())?;

        Ok(Self {
            conn: Mutex::new(conn),
        })
    }
}

impl CacheEngine for RustSQLiteCacheEngine {
    fn clear(&self) -> Result<(), String> {
        let conn = self.conn.lock().unwrap();
        let mut attempts = 0;
        loop {
            let sql = "
                DROP TABLE IF EXISTS files;
                DROP TABLE IF EXISTS scanned_directories;
                CREATE TABLE IF NOT EXISTS files (
                    path TEXT PRIMARY KEY,
                    size INTEGER,
                    mtime_ns INTEGER,
                    entry_dt DATETIME,
                    digest BLOB,
                    digest_partial BLOB,
                    digest_samples BLOB
                );
                CREATE TABLE IF NOT EXISTS scanned_directories (
                    path TEXT PRIMARY KEY,
                    scan_dt DATETIME
                );
                CREATE INDEX IF NOT EXISTS idx_files_size ON files (size);
            ";
            match conn.execute_batch(sql) {
                Ok(_) => break,
                Err(e) => {
                    attempts += 1;
                    if attempts >= 10 {
                        return Err(e.to_string());
                    }
                    std::thread::sleep(std::time::Duration::from_millis(200));
                }
            }
        }
        Ok(())
    }

    fn close(&self) -> Result<(), String> {
        Ok(())
    }

    fn commit(&self) -> Result<(), String> {
        Ok(())
    }

    fn mark_directory_scanned(&self, dir_path: &str) -> Result<(), String> {
        let conn = self.conn.lock().unwrap();
        conn.execute(
            "INSERT INTO scanned_directories (path, scan_dt)
             VALUES (?1, datetime('now'))
             ON CONFLICT(path) DO UPDATE SET scan_dt=datetime('now')",
            params![dir_path],
        )
        .map_err(|e| e.to_string())?;
        Ok(())
    }

    fn is_directory_scanned(&self, dir_path: &str) -> Result<bool, String> {
        let conn = self.conn.lock().unwrap();
        let mut stmt = conn
            .prepare("SELECT 1 FROM scanned_directories WHERE path = ?1")
            .map_err(|e| e.to_string())?;
        let exists = stmt.exists(params![dir_path]).map_err(|e| e.to_string())?;
        Ok(exists)
    }

    fn snapshot_file(&self, path: &str, size: u64, mtime: f64) -> Result<(), String> {
        let conn = self.conn.lock().unwrap();
        let mtime_ns = (mtime * 1e9) as i64;
        conn.execute(
            "INSERT INTO files (path, size, mtime_ns, entry_dt)
             VALUES (?1, ?2, ?3, datetime('now'))
             ON CONFLICT(path) DO UPDATE SET size=?2, mtime_ns=?3, entry_dt=datetime('now')",
            params![path, size as i64, mtime_ns],
        )
        .map_err(|e| e.to_string())?;
        Ok(())
    }

    fn snapshot_files_batch(&self, batch: &[(String, u64, f64)]) -> Result<(), String> {
        let mut conn = self.conn.lock().unwrap();
        let tx = conn.transaction().map_err(|e| e.to_string())?;
        {
            let mut stmt = tx
                .prepare(
                    "INSERT INTO files (path, size, mtime_ns, entry_dt)
                     VALUES (?1, ?2, ?3, datetime('now'))
                     ON CONFLICT(path) DO UPDATE SET size=?2, mtime_ns=?3, entry_dt=datetime('now')",
                )
                .map_err(|e| e.to_string())?;

            for (path, size, mtime) in batch {
                let mtime_ns = (mtime * 1e9) as i64;
                stmt.execute(params![path, *size as i64, mtime_ns])
                    .map_err(|e| e.to_string())?;
            }
        }
        tx.commit().map_err(|e| e.to_string())?;
        Ok(())
    }

    fn get_files_in_directory_page(
        &self,
        dir_path: &str,
        last_path: &str,
        limit: usize,
    ) -> Result<Vec<FileMetadata>, String> {
        let conn = self.conn.lock().unwrap();
        let prefix = format!("{}{}", dir_path, std::path::MAIN_SEPARATOR);
        let prefix_end = format!("{}\u{10ffff}", prefix);

        let mut results = Vec::new();
        if last_path.is_empty() {
            let mut stmt = conn
                .prepare(
                    "SELECT path, size, mtime_ns, entry_dt, digest, digest_partial, digest_samples
                     FROM (
                         SELECT path, size, mtime_ns, entry_dt, digest, digest_partial, digest_samples
                         FROM files
                         WHERE path = ?1
                         UNION ALL
                         SELECT path, size, mtime_ns, entry_dt, digest, digest_partial, digest_samples
                         FROM files
                         WHERE path >= ?2 AND path < ?3
                     )
                     ORDER BY path
                     LIMIT ?4",
                )
                .map_err(|e| e.to_string())?;

            let rows = stmt
                .query_map(
                    params![dir_path, prefix, prefix_end, limit],
                    |row| {
                        Ok(FileMetadata {
                            path: row.get(0)?,
                            size: row.get(1)?,
                            mtime_ns: row.get(2)?,
                            entry_dt: row.get(3)?,
                            digest: row.get(4)?,
                            digest_partial: row.get(5)?,
                            digest_samples: row.get(6)?,
                        })
                    },
                )
                .map_err(|e| e.to_string())?;

            for r in rows {
                results.push(r.map_err(|e| e.to_string())?);
            }
        } else {
            let mut stmt = conn
                .prepare(
                    "SELECT path, size, mtime_ns, entry_dt, digest, digest_partial, digest_samples
                     FROM files
                     WHERE path > ?1 AND path < ?2
                     ORDER BY path
                     LIMIT ?3",
                )
                .map_err(|e| e.to_string())?;

            let rows = stmt
                .query_map(
                    params![last_path, prefix_end, limit],
                    |row| {
                        Ok(FileMetadata {
                            path: row.get(0)?,
                            size: row.get(1)?,
                            mtime_ns: row.get(2)?,
                            entry_dt: row.get(3)?,
                            digest: row.get(4)?,
                            digest_partial: row.get(5)?,
                            digest_samples: row.get(6)?,
                        })
                    },
                )
                .map_err(|e| e.to_string())?;

            for r in rows {
                results.push(r.map_err(|e| e.to_string())?);
            }
        }

        Ok(results)
    }

    fn get_candidate_sizes(&self) -> Result<Vec<u64>, String> {
        let conn = self.conn.lock().unwrap();
        let mut stmt = conn
            .prepare("SELECT size FROM files GROUP BY size HAVING COUNT(*) > 1 AND size > 0")
            .map_err(|e| e.to_string())?;
        let rows = stmt
            .query_map([], |row| {
                let val: i64 = row.get(0)?;
                Ok(val as u64)
            })
            .map_err(|e| e.to_string())?;
        let mut sizes = Vec::new();
        for r in rows {
            sizes.push(r.map_err(|e| e.to_string())?);
        }
        Ok(sizes)
    }

    fn get_files_by_sizes_page(
        &self,
        sizes: &[u64],
        last_path: &str,
        limit: usize,
    ) -> Result<Vec<FileMetadata>, String> {
        if sizes.is_empty() {
            return Ok(Vec::new());
        }
        let conn = self.conn.lock().unwrap();
        let placeholders: Vec<String> = (0..sizes.len()).map(|_| "?".to_string()).collect();
        let sql = format!(
            "SELECT path, size, mtime_ns, entry_dt, digest, digest_partial, digest_samples
             FROM files WHERE size IN ({}) AND path > ? ORDER BY path LIMIT ?",
            placeholders.join(",")
        );
        let mut stmt = conn.prepare(&sql).map_err(|e| e.to_string())?;

        let mut params_vec: Vec<Box<dyn rusqlite::ToSql>> = Vec::new();
        for &s in sizes {
            params_vec.push(Box::new(s as i64));
        }
        params_vec.push(Box::new(last_path.to_string()));
        params_vec.push(Box::new(limit as i64));

        let params_refs: Vec<&dyn rusqlite::ToSql> = params_vec.iter().map(|p| p.as_ref()).collect();

        let rows = stmt
            .query_map(&*params_refs, |row| {
                Ok(FileMetadata {
                    path: row.get(0)?,
                    size: row.get(1)?,
                    mtime_ns: row.get(2)?,
                    entry_dt: row.get(3)?,
                    digest: row.get(4)?,
                    digest_partial: row.get(5)?,
                    digest_samples: row.get(6)?,
                })
            })
            .map_err(|e| e.to_string())?;

        let mut results = Vec::new();
        for r in rows {
            results.push(r.map_err(|e| e.to_string())?);
        }
        Ok(results)
    }

    fn get(
        &self,
        path: &str,
        key: &str,
        size: u64,
        mtime_ns: u64,
        ignore_mtime: bool,
    ) -> Result<Option<Vec<u8>>, String> {
        let conn = self.conn.lock().unwrap();
        let sql = if ignore_mtime {
            format!("SELECT {} FROM files WHERE path=?1 AND size=?2", key)
        } else {
            format!("SELECT {} FROM files WHERE path=?1 AND size=?2 AND mtime_ns=?3", key)
        };

        let mut stmt = conn.prepare(&sql).map_err(|e| e.to_string())?;
        let mut rows = if ignore_mtime {
            stmt.query(params![path, size as i64]).map_err(|e| e.to_string())?
        } else {
            stmt.query(params![path, size as i64, mtime_ns as i64])
                .map_err(|e| e.to_string())?
        };

        if let Some(row) = rows.next().map_err(|e| e.to_string())? {
            let val: Option<Vec<u8>> = row.get(0).map_err(|e| e.to_string())?;
            Ok(val)
        } else {
            Ok(None)
        }
    }

    fn put(&self, path: &str, size: u64, mtime_ns: u64, key: &str, value: &[u8]) -> Result<(), String> {
        let conn = self.conn.lock().unwrap();
        let sql = format!(
            "INSERT INTO files (path, size, mtime_ns, entry_dt, {})
             VALUES (?1, ?2, ?3, datetime('now'), ?4)
             ON CONFLICT(path) DO UPDATE SET size=?2, mtime_ns=?3, entry_dt=datetime('now'), {}=?4",
            key, key
        );
        conn.execute(&sql, params![path, size as i64, mtime_ns as i64, value])
            .map_err(|e| e.to_string())?;
        Ok(())
    }

    fn get_cache_viewer_files(
        &self,
        search: Option<&str>,
        limit: usize,
        offset: usize,
    ) -> Result<(usize, Vec<FileMetadata>), String> {
        let conn = self.conn.lock().unwrap();
        let (total_count, rows_stmt) = match search {
            Some(s) if !s.is_empty() => {
                let search_pat = format!("%{}%", s);
                let count: i64 = conn
                    .query_row(
                        "SELECT COUNT(*) FROM files WHERE path LIKE ?1",
                        params![search_pat],
                        |row| row.get(0),
                    )
                    .map_err(|e| e.to_string())?;
                let mut stmt = conn
                    .prepare(
                        "SELECT path, size, mtime_ns, entry_dt, digest, digest_partial, digest_samples
                     FROM files WHERE path LIKE ?1
                     ORDER BY entry_dt DESC LIMIT ?2 OFFSET ?3",
                    )
                    .map_err(|e| e.to_string())?;
                let rows = stmt
                    .query_map(params![search_pat, limit, offset], |row| {
                        Ok(FileMetadata {
                            path: row.get(0)?,
                            size: row.get(1)?,
                            mtime_ns: row.get(2)?,
                            entry_dt: row.get(3)?,
                            digest: row.get(4)?,
                            digest_partial: row.get(5)?,
                            digest_samples: row.get(6)?,
                        })
                    })
                    .map_err(|e| e.to_string())?;
                let mut results = Vec::new();
                for r in rows {
                    results.push(r.map_err(|e| e.to_string())?);
                }
                (count as usize, results)
            }
            _ => {
                let count: i64 = conn
                    .query_row("SELECT COUNT(*) FROM files", [], |row| row.get(0))
                    .map_err(|e| e.to_string())?;
                let mut stmt = conn
                    .prepare(
                        "SELECT path, size, mtime_ns, entry_dt, digest, digest_partial, digest_samples
                     FROM files
                     ORDER BY entry_dt DESC LIMIT ?1 OFFSET ?2",
                    )
                    .map_err(|e| e.to_string())?;
                let rows = stmt
                    .query_map(params![limit, offset], |row| {
                        Ok(FileMetadata {
                            path: row.get(0)?,
                            size: row.get(1)?,
                            mtime_ns: row.get(2)?,
                            entry_dt: row.get(3)?,
                            digest: row.get(4)?,
                            digest_partial: row.get(5)?,
                            digest_samples: row.get(6)?,
                        })
                    })
                    .map_err(|e| e.to_string())?;
                let mut results = Vec::new();
                for r in rows {
                    results.push(r.map_err(|e| e.to_string())?);
                }
                (count as usize, results)
            }
        };
        Ok((total_count, rows_stmt))
    }
}

// ==========================================
// Valkey / Redis Cache Engine Implementation
// ==========================================

pub struct RustValkeyCacheEngine {
    conn: Mutex<redis::Connection>,
}

impl RustValkeyCacheEngine {
    pub fn new(url: &str) -> Result<Self, String> {
        let client = redis::Client::open(url).map_err(|e| e.to_string())?;
        let conn = client.get_connection().map_err(|e| e.to_string())?;
        Ok(Self {
            conn: Mutex::new(conn),
        })
    }
}

impl CacheEngine for RustValkeyCacheEngine {
    fn clear(&self) -> Result<(), String> {
        let mut conn_guard = self.conn.lock().unwrap();
        let conn = &mut *conn_guard;

        if redis::cmd("FLUSHDB").query::<()>(conn).is_ok()
            || redis::cmd("FLUSHDB").arg("ASYNC").query::<()>(conn).is_ok()
        {
            return Ok(());
        }

        let mut cursor: u64 = 0;
        loop {
            let res: Result<(u64, Vec<String>), _> = redis::cmd("SCAN")
                .arg(cursor)
                .arg("MATCH")
                .arg("dg:*")
                .arg("COUNT")
                .arg(1000)
                .query(conn);

            match res {
                Ok((next_cursor, keys)) => {
                    if !keys.is_empty() {
                        let _: () = redis::cmd("DEL")
                            .arg(&keys)
                            .query(conn)
                            .map_err(|e| e.to_string())?;
                    }
                    cursor = next_cursor;
                    if cursor == 0 {
                        break;
                    }
                }
                Err(e) => return Err(e.to_string()),
            }
        }
        Ok(())
    }

    fn close(&self) -> Result<(), String> {
        Ok(())
    }

    fn commit(&self) -> Result<(), String> {
        Ok(())
    }

    fn mark_directory_scanned(&self, dir_path: &str) -> Result<(), String> {
        let mut conn_guard = self.conn.lock().unwrap();
        let conn = &mut *conn_guard;
        let _: () = redis::cmd("SADD")
            .arg("dg:scanned_dirs")
            .arg(dir_path)
            .query(conn)
            .map_err(|e| e.to_string())?;
        Ok(())
    }

    fn is_directory_scanned(&self, dir_path: &str) -> Result<bool, String> {
        let mut conn_guard = self.conn.lock().unwrap();
        let conn = &mut *conn_guard;
        let exists: bool = redis::cmd("SISMEMBER")
            .arg("dg:scanned_dirs")
            .arg(dir_path)
            .query(conn)
            .map_err(|e| e.to_string())?;
        Ok(exists)
    }

    fn snapshot_file(&self, path: &str, size: u64, mtime: f64) -> Result<(), String> {
        let mut conn_guard = self.conn.lock().unwrap();
        let conn = &mut *conn_guard;
        let mtime_ns = (mtime * 1e9) as i64;
        let file_key = format!("dg:file:{}", path);

        let old_size_str: Option<String> = redis::cmd("HGET")
            .arg(&file_key)
            .arg("size")
            .query(conn)
            .map_err(|e| e.to_string())?;
        let old_size = old_size_str.and_then(|s| s.parse::<u64>().ok());

        let now_str = chrono::Local::now().to_rfc3339();

        let mut pipe = redis::pipe();
        pipe.cmd("HSET").arg(&file_key).arg("size").arg(size);
        pipe.cmd("HSET").arg(&file_key).arg("mtime_ns").arg(mtime_ns);
        pipe.cmd("HSET").arg(&file_key).arg("entry_dt").arg(&now_str);
        pipe.cmd("ZADD").arg("dg:files_by_path").arg(0).arg(path);
        pipe.cmd("ZADD").arg("dg:files_by_entry_dt").arg(mtime).arg(path);

        let _: () = pipe.query(conn).map_err(|e| e.to_string())?;

        if old_size != Some(size) {
            if let Some(os) = old_size {
                let _: () = redis::cmd("SREM")
                    .arg(format!("dg:size_files:{}", os))
                    .arg(path)
                    .query(conn)
                    .map_err(|e| e.to_string())?;
                let dec_count: i64 = redis::cmd("HINCRBY")
                    .arg("dg:size_counts")
                    .arg(os.to_string())
                    .arg(-1)
                    .query(conn)
                    .map_err(|e| e.to_string())?;
                if dec_count < 2 {
                    let _: () = redis::cmd("SREM")
                        .arg("dg:candidate_sizes")
                        .arg(os)
                        .query(conn)
                        .map_err(|e| e.to_string())?;
                }
            }
            let _: () = redis::cmd("SADD")
                .arg(format!("dg:size_files:{}", size))
                .arg(path)
                .query(conn)
                .map_err(|e| e.to_string())?;
            let inc_count: i64 = redis::cmd("HINCRBY")
                .arg("dg:size_counts")
                .arg(size.to_string())
                .arg(1)
                .query(conn)
                .map_err(|e| e.to_string())?;
            if inc_count >= 2 {
                let _: () = redis::cmd("SADD")
                    .arg("dg:candidate_sizes")
                    .arg(size)
                    .query(conn)
                    .map_err(|e| e.to_string())?;
            }
        }

        Ok(())
    }

    fn snapshot_files_batch(&self, batch: &[(String, u64, f64)]) -> Result<(), String> {
        let mut conn_guard = self.conn.lock().unwrap();
        let conn = &mut *conn_guard;
        let mut pipe = redis::pipe();
        let now_str = chrono::Utc::now().to_rfc3339();

        for (path, size, mtime) in batch {
            let mtime_ns = (mtime * 1e9) as u64;
            let file_key = format!("dg:file:{}", path);
            pipe.cmd("HMSET")
                .arg(&file_key)
                .arg("size")
                .arg(size)
                .arg("mtime_ns")
                .arg(mtime_ns)
                .arg("entry_dt")
                .arg(&now_str);
            pipe.cmd("ZADD").arg("dg:files_by_path").arg(0).arg(path);
            pipe.cmd("SADD").arg(format!("dg:size_files:{}", size)).arg(path);
        }

        let _: () = pipe.query(conn).map_err(|e| e.to_string())?;
        Ok(())
    }

    fn get_files_in_directory_page(
        &self,
        dir_path: &str,
        last_path: &str,
        limit: usize,
    ) -> Result<Vec<FileMetadata>, String> {
        let mut conn_guard = self.conn.lock().unwrap();
        let conn = &mut *conn_guard;
        let prefix = format!("{}{}", dir_path, std::path::MAIN_SEPARATOR);

        let mut results = Vec::new();

        if last_path.is_empty() {
            let dir_key = format!("dg:file:{}", dir_path);
            let dir_exists: bool = redis::cmd("EXISTS")
                .arg(&dir_key)
                .query(conn)
                .map_err(|e| e.to_string())?;

            if dir_exists {
                let meta: Vec<Option<Vec<u8>>> = redis::cmd("HMGET")
                    .arg(&dir_key)
                    .arg("size")
                    .arg("mtime_ns")
                    .arg("entry_dt")
                    .arg("digest")
                    .arg("digest_partial")
                    .arg("digest_samples")
                    .query(conn)
                    .map_err(|e| e.to_string())?;
                if let (Some(size_bytes), Some(mtime_bytes)) = (&meta[0], &meta[1]) {
                    let size = String::from_utf8_lossy(size_bytes).parse::<u64>().unwrap_or(0);
                    let mtime_ns = String::from_utf8_lossy(mtime_bytes).parse::<u64>().unwrap_or(0);
                    results.push(FileMetadata {
                        path: dir_path.to_string(),
                        size,
                        mtime_ns,
                        entry_dt: meta[2]
                            .as_ref()
                            .map(|b| String::from_utf8_lossy(b).into_owned())
                            .unwrap_or_default(),
                        digest: meta[3].clone(),
                        digest_partial: meta[4].clone(),
                        digest_samples: meta[5].clone(),
                    });
                }
            }
        }

        let min_bound = if last_path.is_empty() {
            let mut b = vec![b'['];
            b.extend_from_slice(prefix.as_bytes());
            b
        } else {
            let mut b = vec![b'('];
            b.extend_from_slice(last_path.as_bytes());
            b
        };

        let mut max_bound = vec![b'['];
        max_bound.extend_from_slice(prefix.as_bytes());
        max_bound.push(0xff);

        let path_bytes_list: Vec<Vec<u8>> = redis::cmd("ZRANGEBYLEX")
            .arg("dg:files_by_path")
            .arg(min_bound)
            .arg(max_bound)
            .arg("LIMIT")
            .arg(0)
            .arg(limit)
            .query(conn)
            .map_err(|e| e.to_string())?;

        let mut pipe = redis::pipe();
        for p_bytes in &path_bytes_list {
            let p_str = String::from_utf8_lossy(p_bytes);
            let file_key = format!("dg:file:{}", p_str);
            pipe.cmd("HMGET")
                .arg(&file_key)
                .arg("size")
                .arg("mtime_ns")
                .arg("entry_dt")
                .arg("digest")
                .arg("digest_partial")
                .arg("digest_samples");
        }

        let pipeline_results: Vec<Vec<Option<Vec<u8>>>> = pipe.query(conn).map_err(|e| e.to_string())?;

        for (p_bytes, meta) in path_bytes_list.iter().zip(pipeline_results) {
            let p_str = String::from_utf8_lossy(p_bytes).into_owned();
            if meta.len() >= 2 {
                if let (Some(size_bytes), Some(mtime_bytes)) = (&meta[0], &meta[1]) {
                    let size = String::from_utf8_lossy(size_bytes).parse::<u64>().unwrap_or(0);
                    let mtime_ns = String::from_utf8_lossy(mtime_bytes).parse::<u64>().unwrap_or(0);
                    results.push(FileMetadata {
                        path: p_str,
                        size,
                        mtime_ns,
                        entry_dt: meta[2]
                            .as_ref()
                            .map(|b| String::from_utf8_lossy(b).into_owned())
                            .unwrap_or_default(),
                        digest: meta[3].clone(),
                        digest_partial: meta[4].clone(),
                        digest_samples: meta[5].clone(),
                    });
                }
            }
        }

        Ok(results)
    }

    fn get_candidate_sizes(&self) -> Result<Vec<u64>, String> {
        let mut conn_guard = self.conn.lock().unwrap();
        let conn = &mut *conn_guard;
        let sizes: std::collections::HashSet<String> = redis::cmd("SMEMBERS")
            .arg("dg:candidate_sizes")
            .query(conn)
            .map_err(|e| e.to_string())?;
        let res = sizes.into_iter().filter_map(|s| s.parse::<u64>().ok()).collect();
        Ok(res)
    }

    fn get_files_by_sizes_page(
        &self,
        sizes: &[u64],
        last_path: &str,
        limit: usize,
    ) -> Result<Vec<FileMetadata>, String> {
        let mut conn_guard = self.conn.lock().unwrap();
        let conn = &mut *conn_guard;
        let mut all_paths = std::collections::BTreeSet::new();
        for &size in sizes {
            let paths: std::collections::HashSet<String> = redis::cmd("SMEMBERS")
                .arg(format!("dg:size_files:{}", size))
                .query(conn)
                .map_err(|e| e.to_string())?;
            all_paths.extend(paths);
        }

        let mut results = Vec::new();
        let range = if last_path.is_empty() {
            all_paths.range::<str, _>(..).take(limit)
        } else {
            all_paths
                .range::<str, _>((Excluded(last_path), Unbounded))
                .take(limit)
        };

        let mut pipe = redis::pipe();
        let paths_vec: Vec<String> = range.cloned().collect();
        for path in &paths_vec {
            let file_key = format!("dg:file:{}", path);
            pipe.cmd("HMGET")
                .arg(&file_key)
                .arg("size")
                .arg("mtime_ns")
                .arg("entry_dt")
                .arg("digest")
                .arg("digest_partial")
                .arg("digest_samples");
        }

        let pipeline_results: Vec<Vec<Option<Vec<u8>>>> = pipe.query(conn).map_err(|e| e.to_string())?;

        for (path, meta) in paths_vec.into_iter().zip(pipeline_results) {
            if meta.len() >= 2 {
                if let (Some(size_bytes), Some(mtime_bytes)) = (&meta[0], &meta[1]) {
                    let size_val = String::from_utf8_lossy(size_bytes).parse::<u64>().unwrap_or(0);
                    let mtime_ns = String::from_utf8_lossy(mtime_bytes).parse::<u64>().unwrap_or(0);
                    results.push(FileMetadata {
                        path,
                        size: size_val,
                        mtime_ns,
                        entry_dt: meta[2]
                            .as_ref()
                            .map(|b| String::from_utf8_lossy(b).into_owned())
                            .unwrap_or_default(),
                        digest: meta[3].clone(),
                        digest_partial: meta[4].clone(),
                        digest_samples: meta[5].clone(),
                    });
                }
            }
        }
        Ok(results)
    }

    fn get(
        &self,
        path: &str,
        key: &str,
        size: u64,
        mtime_ns: u64,
        ignore_mtime: bool,
    ) -> Result<Option<Vec<u8>>, String> {
        let mut conn_guard = self.conn.lock().unwrap();
        let conn = &mut *conn_guard;
        let file_key = format!("dg:file:{}", path);
        let meta: Vec<Option<Vec<u8>>> = redis::cmd("HMGET")
            .arg(&file_key)
            .arg("size")
            .arg("mtime_ns")
            .arg(key)
            .query(conn)
            .map_err(|e| e.to_string())?;

        let db_size = meta[0]
            .as_ref()
            .and_then(|b| String::from_utf8_lossy(b).parse::<u64>().ok());
        let db_mtime = meta[1]
            .as_ref()
            .and_then(|b| String::from_utf8_lossy(b).parse::<u64>().ok());

        if db_size == Some(size) && (ignore_mtime || db_mtime == Some(mtime_ns)) {
            Ok(meta[2].clone())
        } else {
            Ok(None)
        }
    }

    fn put(&self, path: &str, size: u64, mtime_ns: u64, key: &str, value: &[u8]) -> Result<(), String> {
        let mut conn_guard = self.conn.lock().unwrap();
        let conn = &mut *conn_guard;
        let file_key = format!("dg:file:{}", path);

        let now_str = chrono::Local::now().to_rfc3339();
        let mut pipe = redis::pipe();
        pipe.cmd("HSET").arg(&file_key).arg("size").arg(size);
        pipe.cmd("HSET").arg(&file_key).arg("mtime_ns").arg(mtime_ns);
        pipe.cmd("HSET").arg(&file_key).arg("entry_dt").arg(&now_str);
        pipe.cmd("HSET").arg(&file_key).arg(key).arg(value);
        pipe.cmd("ZADD").arg("dg:files_by_path").arg(0).arg(path);
        pipe.cmd("ZADD").arg("dg:files_by_entry_dt").arg((mtime_ns as f64) / 1e9).arg(path);

        let _: () = pipe.query(conn).map_err(|e| e.to_string())?;
        Ok(())
    }

    fn get_cache_viewer_files(
        &self,
        search: Option<&str>,
        limit: usize,
        offset: usize,
    ) -> Result<(usize, Vec<FileMetadata>), String> {
        let mut conn_guard = self.conn.lock().unwrap();
        let conn = &mut *conn_guard;
        let mut results = Vec::new();

        match search {
            Some(s) if !s.is_empty() => {
                let all_paths_bytes: Vec<Vec<u8>> = redis::cmd("ZREVRANGE")
                    .arg("dg:files_by_entry_dt")
                    .arg(0)
                    .arg(-1)
                    .query(conn)
                    .map_err(|e| e.to_string())?;
                let mut matched_paths = Vec::new();
                for p_bytes in all_paths_bytes {
                    let p_str = String::from_utf8_lossy(&p_bytes).into_owned();
                    if p_str.contains(s) {
                        matched_paths.push(p_str);
                    }
                }
                let total_count = matched_paths.len();
                let end = std::cmp::min(offset + limit, total_count);
                if offset < total_count {
                    for path in &matched_paths[offset..end] {
                        let file_key = format!("dg:file:{}", path);
                        let meta: Vec<Option<Vec<u8>>> = redis::cmd("HMGET")
                            .arg(&file_key)
                            .arg("size")
                            .arg("mtime_ns")
                            .arg("entry_dt")
                            .arg("digest")
                            .arg("digest_partial")
                            .arg("digest_samples")
                            .query(conn)
                            .map_err(|e| e.to_string())?;
                        if let (Some(size_bytes), Some(mtime_bytes)) = (&meta[0], &meta[1]) {
                            let size = String::from_utf8_lossy(size_bytes).parse::<u64>().unwrap_or(0);
                            let mtime_ns = String::from_utf8_lossy(mtime_bytes).parse::<u64>().unwrap_or(0);
                            results.push(FileMetadata {
                                path: path.clone(),
                                size,
                                mtime_ns,
                                entry_dt: meta[2]
                                    .as_ref()
                                    .map(|b| String::from_utf8_lossy(b).into_owned())
                                    .unwrap_or_default(),
                                digest: meta[3].clone(),
                                digest_partial: meta[4].clone(),
                                digest_samples: meta[5].clone(),
                            });
                        }
                    }
                }
                Ok((total_count, results))
            }
            _ => {
                let total_count: usize = redis::cmd("ZCARD")
                    .arg("dg:files_by_entry_dt")
                    .query(conn)
                    .map_err(|e| e.to_string())?;
                let path_bytes_list: Vec<Vec<u8>> = redis::cmd("ZREVRANGE")
                    .arg("dg:files_by_entry_dt")
                    .arg(offset)
                    .arg(offset + limit - 1)
                    .query(conn)
                    .map_err(|e| e.to_string())?;
                for p_bytes in path_bytes_list {
                    let p_str = String::from_utf8_lossy(&p_bytes).into_owned();
                    let file_key = format!("dg:file:{}", p_str);
                    let meta: Vec<Option<Vec<u8>>> = redis::cmd("HMGET")
                        .arg(&file_key)
                        .arg("size")
                        .arg("mtime_ns")
                        .arg("entry_dt")
                        .arg("digest")
                        .arg("digest_partial")
                        .arg("digest_samples")
                        .query(conn)
                        .map_err(|e| e.to_string())?;
                    if let (Some(size_bytes), Some(mtime_bytes)) = (&meta[0], &meta[1]) {
                        let size = String::from_utf8_lossy(size_bytes).parse::<u64>().unwrap_or(0);
                        let mtime_ns = String::from_utf8_lossy(mtime_bytes).parse::<u64>().unwrap_or(0);
                        results.push(FileMetadata {
                            path: p_str,
                            size,
                            mtime_ns,
                            entry_dt: meta[2]
                                .as_ref()
                                .map(|b| String::from_utf8_lossy(b).into_owned())
                                .unwrap_or_default(),
                            digest: meta[3].clone(),
                            digest_partial: meta[4].clone(),
                            digest_samples: meta[5].clone(),
                        });
                    }
                }
                Ok((total_count, results))
            }
        }
    }
}

// ==========================================
// PyO3 Native Module Interface
// ==========================================

#[pyclass]
pub struct RustFilesDB {
    engine: Box<dyn CacheEngine + Send + Sync>,
}

#[pymethods]
impl RustFilesDB {
    #[new]
    pub fn new(cache_url: String) -> PyResult<Self> {
        let engine: Box<dyn CacheEngine + Send + Sync> =
            if cache_url.starts_with("redis://")
                || cache_url.starts_with("valkey://")
                || cache_url.starts_with("rediss://")
            {
                let eng = RustValkeyCacheEngine::new(&cache_url)
                    .map_err(|e| PyValueError::new_err(format!("Redis connection error: {}", e)))?;
                Box::new(eng)
            } else {
                let eng = RustSQLiteCacheEngine::new(&cache_url)
                    .map_err(|e| PyValueError::new_err(format!("SQLite connection error: {}", e)))?;
                Box::new(eng)
            };
        Ok(Self { engine })
    }

    pub fn clear(&self) -> PyResult<()> {
        self.engine.clear().map_err(PyValueError::new_err)
    }

    pub fn close(&self) -> PyResult<()> {
        self.engine.close().map_err(PyValueError::new_err)
    }

    pub fn commit(&self) -> PyResult<()> {
        self.engine.commit().map_err(PyValueError::new_err)
    }

    pub fn mark_directory_scanned(&self, dir_path: String) -> PyResult<()> {
        self.engine
            .mark_directory_scanned(&dir_path)
            .map_err(PyValueError::new_err)
    }

    pub fn is_directory_scanned(&self, dir_path: String) -> PyResult<bool> {
        self.engine
            .is_directory_scanned(&dir_path)
            .map_err(PyValueError::new_err)
    }

    pub fn snapshot_file(&self, path: String, size: u64, mtime: f64) -> PyResult<()> {
        self.engine
            .snapshot_file(&path, size, mtime)
            .map_err(PyValueError::new_err)
    }

    pub fn snapshot_files_batch(&self, batch: Vec<(String, u64, f64)>) -> PyResult<()> {
        self.engine
            .snapshot_files_batch(&batch)
            .map_err(PyValueError::new_err)
    }

    pub fn get_files_in_directory_page<'py>(
        &self,
        py: Python<'py>,
        dir_path: String,
        last_path: String,
        limit: usize,
    ) -> PyResult<Vec<Bound<'py, PyDict>>> {
        let files = self
            .engine
            .get_files_in_directory_page(&dir_path, &last_path, limit)
            .map_err(PyValueError::new_err)?;
        let mut py_files = Vec::with_capacity(files.len());
        for f in files {
            py_files.push(file_metadata_to_dict(py, &f)?);
        }
        Ok(py_files)
    }

    pub fn get_candidate_sizes(&self) -> PyResult<Vec<u64>> {
        self.engine.get_candidate_sizes().map_err(PyValueError::new_err)
    }

    pub fn get_files_by_sizes_page<'py>(
        &self,
        py: Python<'py>,
        sizes: Vec<u64>,
        last_path: String,
        limit: usize,
    ) -> PyResult<Vec<Bound<'py, PyDict>>> {
        let files = self
            .engine
            .get_files_by_sizes_page(&sizes, &last_path, limit)
            .map_err(PyValueError::new_err)?;
        let mut py_files = Vec::with_capacity(files.len());
        for f in files {
            py_files.push(file_metadata_to_dict(py, &f)?);
        }
        Ok(py_files)
    }

    pub fn get<'py>(
        &self,
        py: Python<'py>,
        path: String,
        key: String,
        size: u64,
        mtime_ns: u64,
        ignore_mtime: bool,
    ) -> PyResult<Option<Bound<'py, PyBytes>>> {
        let bytes_opt = self
            .engine
            .get(&path, &key, size, mtime_ns, ignore_mtime)
            .map_err(PyValueError::new_err)?;
        match bytes_opt {
            Some(b) => Ok(Some(PyBytes::new(py, &b))),
            None => Ok(None),
        }
    }

    pub fn put(&self, path: String, size: u64, mtime_ns: u64, key: String, value: &Bound<'_, PyBytes>) -> PyResult<()> {
        self.engine
            .put(&path, size, mtime_ns, &key, value.as_bytes())
            .map_err(PyValueError::new_err)
    }

    #[pyo3(signature = (search=None, limit=20, offset=0))]
    pub fn get_cache_viewer_files<'py>(
        &self,
        py: Python<'py>,
        search: Option<String>,
        limit: usize,
        offset: usize,
    ) -> PyResult<(usize, Vec<Bound<'py, PyDict>>)> {
        let (total, files) = self
            .engine
            .get_cache_viewer_files(search.as_deref(), limit, offset)
            .map_err(PyValueError::new_err)?;
        let mut py_files = Vec::with_capacity(files.len());
        for f in files {
            py_files.push(file_metadata_to_dict(py, &f)?);
        }
        Ok((total, py_files))
    }
}

// ==========================================
// Phase 2: Parallel Crawler & Hasher Engine
// ==========================================

#[pyfunction]
#[pyo3(signature = (roots, min_size=0, max_size=None))]
pub fn collect_files_parallel(
    roots: Vec<String>,
    min_size: u64,
    max_size: Option<u64>,
) -> PyResult<Vec<(String, u64, f64)>> {
    use rayon::prelude::*;
    use walkdir::WalkDir;

    let results: Vec<(String, u64, f64)> = roots
        .into_par_iter()
        .flat_map(|root| {
            let mut files = Vec::new();
            for entry in WalkDir::new(root).into_iter().filter_map(|e| e.ok()) {
                if entry.file_type().is_file() {
                    if let Ok(meta) = entry.metadata() {
                        let size = meta.len();
                        if size >= min_size && max_size.map_or(true, |max| size <= max) {
                            let path_str = entry.path().to_string_lossy().to_string();
                            let mtime = meta
                                .modified()
                                .ok()
                                .and_then(|t| t.duration_since(std::time::UNIX_EPOCH).ok())
                                .map(|d| d.as_secs_f64())
                                .unwrap_or(0.0);
                            files.push((path_str, size, mtime));
                        }
                    }
                }
            }
            files
        })
        .collect();
    Ok(results)
}

#[pyfunction]
#[pyo3(signature = (paths_and_sizes, sample_size=0))]
pub fn hash_files_parallel(
    paths_and_sizes: Vec<(String, u64)>,
    sample_size: usize,
) -> PyResult<Vec<(String, String)>> {
    use rayon::prelude::*;
    use std::fs::File;
    use std::io::{BufReader, Read, Seek};

    let results: Vec<(String, String)> = paths_and_sizes
        .into_par_iter()
        .map(|(path, size)| {
            let digest = match File::open(&path) {
                Ok(file) => {
                    let mut reader = BufReader::new(file);
                    if sample_size > 0 && (size as usize) > sample_size * 2 {
                        let mut head_buf = vec![0u8; sample_size];
                        let mut tail_buf = vec![0u8; sample_size];
                        let mut combined = Vec::with_capacity(sample_size * 2);
                        if reader.read_exact(&mut head_buf).is_ok() {
                            combined.extend_from_slice(&head_buf);
                        }
                        if (size as usize) >= sample_size {
                            if reader.seek(std::io::SeekFrom::End(-(sample_size as i64))).is_ok() {
                                if reader.read_exact(&mut tail_buf).is_ok() {
                                    combined.extend_from_slice(&tail_buf);
                                }
                            }
                        }
                        format!("{:x}", md5::compute(&combined))
                    } else {
                        let mut context = md5::Context::new();
                        let mut buf = vec![0u8; 65536];
                        loop {
                            match reader.read(&mut buf) {
                                Ok(0) => break,
                                Ok(n) => context.consume(&buf[..n]),
                                Err(_) => break,
                            }
                        }
                        format!("{:x}", context.compute())
                    }
                }
                Err(_) => String::new(),
            };
            (path, digest)
        })
        .collect();
    Ok(results)
}

#[pyfunction]
#[pyo3(signature = (db_paths))]
pub fn cross_db_compare<'py>(
    py: Python<'py>,
    db_paths: Vec<String>,
) -> PyResult<Vec<Bound<'py, PyDict>>> {
    use rayon::prelude::*;
    use rusqlite::{Connection, OpenFlags};
    use std::collections::{HashMap, HashSet};
    use pyo3::types::PyList;

    let db_files: Vec<(String, Vec<(String, u64, f64, String)>)> = db_paths
        .into_par_iter()
        .filter_map(|db_path| {
            let conn = Connection::open_with_flags(&db_path, OpenFlags::SQLITE_OPEN_READ_ONLY).ok()?;
            let mut stmt = conn
                .prepare("SELECT path, size, mtime_ns, hex(COALESCE(digest, digest_partial)) FROM files WHERE size > 0 AND (digest IS NOT NULL OR digest_partial IS NOT NULL)")
                .ok()?;
            let file_rows = stmt
                .query_map([], |row| {
                    Ok((
                        row.get::<_, String>(0)?,
                        row.get::<_, u64>(1)?,
                        (row.get::<_, f64>(2).or_else(|_| row.get::<_, i64>(2).map(|v| v as f64)).unwrap_or(0.0)) / 1e9,
                        row.get::<_, String>(3).unwrap_or_default(),
                    ))
                })
                .ok()?
                .filter_map(|r| r.ok())
                .collect();
            Some((db_path, file_rows))
        })
        .collect();

    let mut checksum_groups: HashMap<(u64, String), Vec<(String, u64, f64, String, String)>> = HashMap::new();
    for (db_path, files) in db_files {
        for (path, size, mtime, checksum) in files {
            if !checksum.is_empty() {
                checksum_groups
                    .entry((size, checksum.clone()))
                    .or_default()
                    .push((path, size, mtime, checksum, db_path.clone()));
            }
        }
    }

    let mut dupe_groups = Vec::new();
    let mut group_id = 0;

    for ((size, checksum), files) in checksum_groups {
        if files.len() > 1 {
            group_id += 1;
            let mut db_sources = HashSet::new();
            let py_files = PyList::empty(py);

            for (path, file_size, mtime, file_checksum, db_path) in &files {
                db_sources.insert(db_path.clone());
                let db_name = std::path::Path::new(db_path)
                    .file_stem()
                    .and_then(|s| s.to_str())
                    .unwrap_or("");

                let file_dict = PyDict::new(py);
                file_dict.set_item("path", path)?;
                file_dict.set_item("size", *file_size)?;
                file_dict.set_item("mtime_ns", (*mtime * 1e9) as u64)?;
                file_dict.set_item("checksum", file_checksum)?;
                file_dict.set_item("db_path", db_path)?;
                file_dict.set_item("db_name", db_name)?;
                py_files.append(file_dict)?;
            }

            let group_dict = PyDict::new(py);
            group_dict.set_item("group_id", group_id)?;
            group_dict.set_item("size", size)?;
            group_dict.set_item("checksum", &checksum)?;
            group_dict.set_item("match_count", files.len())?;
            group_dict.set_item("db_count", db_sources.len())?;
            group_dict.set_item("files", py_files)?;

            dupe_groups.push(group_dict);
        }
    }

    Ok(dupe_groups)
}

#[pymodule]
fn dupeguru_rust(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<RustFilesDB>()?;
    m.add_function(wrap_pyfunction!(collect_files_parallel, m)?)?;
    m.add_function(wrap_pyfunction!(hash_files_parallel, m)?)?;
    m.add_function(wrap_pyfunction!(cross_db_compare, m)?)?;
    Ok(())
}
