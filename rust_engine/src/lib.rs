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
    let dict = PyDict::new_bound(py);
    dict.set_item("path", &meta.path)?;
    dict.set_item("size", meta.size)?;
    dict.set_item("mtime_ns", meta.mtime_ns)?;
    dict.set_item("entry_dt", &meta.entry_dt)?;

    if let Some(ref d) = meta.digest {
        dict.set_item("digest", PyBytes::new_bound(py, d))?;
    } else {
        dict.set_item("digest", py.None())?;
    }
    if let Some(ref dp) = meta.digest_partial {
        dict.set_item("digest_partial", PyBytes::new_bound(py, dp))?;
    } else {
        dict.set_item("digest_partial", py.None())?;
    }
    if let Some(ref ds) = meta.digest_samples {
        dict.set_item("digest_samples", PyBytes::new_bound(py, ds))?;
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
        conn.execute("DROP TABLE IF EXISTS files;", [])
            .map_err(|e| e.to_string())?;
        conn.execute("DROP TABLE IF EXISTS scanned_directories;", [])
            .map_err(|e| e.to_string())?;

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

    fn get_files_in_directory_page(
        &self,
        dir_path: &str,
        last_path: &str,
        limit: usize,
    ) -> Result<Vec<FileMetadata>, String> {
        let conn = self.conn.lock().unwrap();
        let prefix = format!("{}{}", dir_path, std::path::MAIN_SEPARATOR);

        let mut stmt = conn
            .prepare(
                "SELECT path, size, mtime_ns, entry_dt, digest, digest_partial, digest_samples
                 FROM files
                 WHERE (path = ?1 OR path LIKE ?2) AND path > ?3
                 ORDER BY path
                 LIMIT ?4",
            )
            .map_err(|e| e.to_string())?;

        let rows = stmt
            .query_map(
                params![dir_path, format!("{}%", prefix), last_path, limit],
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

        let mut results = Vec::new();
        for r in rows {
            results.push(r.map_err(|e| e.to_string())?);
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
        let keys: Vec<String> = {
            let iter: redis::Iter<String> = redis::cmd("SCAN")
                .arg(0)
                .arg("MATCH")
                .arg("dg:*")
                .arg("COUNT")
                .arg(1000)
                .clone()
                .iter(conn)
                .map_err(|e| e.to_string())?;
            iter.collect()
        };

        for chunk in keys.chunks(1000) {
            let _: () = redis::cmd("DEL")
                .arg(chunk)
                .query(conn)
                .map_err(|e| e.to_string())?;
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
                let new_count: i64 = redis::cmd("HINCRBY")
                    .arg("dg:size_counts")
                    .arg(os.to_string())
                    .arg(-1)
                    .query(conn)
                    .map_err(|e| e.to_string())?;
                if new_count < 2 {
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
            let new_count: i64 = redis::cmd("HINCRBY")
                .arg("dg:size_counts")
                .arg(size.to_string())
                .arg(1)
                .query(conn)
                .map_err(|e| e.to_string())?;
            if new_count >= 2 {
                let _: () = redis::cmd("SADD")
                    .arg("dg:candidate_sizes")
                    .arg(size)
                    .query(conn)
                    .map_err(|e| e.to_string())?;
            }
        }

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

        for path in range {
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
                let size_val = String::from_utf8_lossy(size_bytes).parse::<u64>().unwrap_or(0);
                let mtime_ns = String::from_utf8_lossy(mtime_bytes).parse::<u64>().unwrap_or(0);
                results.push(FileMetadata {
                    path: path.clone(),
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
    pub fn new(cache_url: &str) -> PyResult<Self> {
        let engine: Box<dyn CacheEngine + Send + Sync> =
            if cache_url.starts_with("redis://") || cache_url.starts_with("rediss://") {
                let eng = RustValkeyCacheEngine::new(cache_url)
                    .map_err(|e| PyValueError::new_err(format!("Redis connection error: {}", e)))?;
                Box::new(eng)
            } else {
                let eng = RustSQLiteCacheEngine::new(cache_url)
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

    pub fn mark_directory_scanned(&self, dir_path: &str) -> PyResult<()> {
        self.engine
            .mark_directory_scanned(dir_path)
            .map_err(PyValueError::new_err)
    }

    pub fn is_directory_scanned(&self, dir_path: &str) -> PyResult<bool> {
        self.engine
            .is_directory_scanned(dir_path)
            .map_err(PyValueError::new_err)
    }

    pub fn snapshot_file(&self, path: &str, size: u64, mtime: f64) -> PyResult<()> {
        self.engine
            .snapshot_file(path, size, mtime)
            .map_err(PyValueError::new_err)
    }

    pub fn get_files_in_directory_page<'py>(
        &self,
        py: Python<'py>,
        dir_path: &str,
        last_path: &str,
        limit: usize,
    ) -> PyResult<Vec<Bound<'py, PyDict>>> {
        let files = self
            .engine
            .get_files_in_directory_page(dir_path, last_path, limit)
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
        last_path: &str,
        limit: usize,
    ) -> PyResult<Vec<Bound<'py, PyDict>>> {
        let files = self
            .engine
            .get_files_by_sizes_page(&sizes, last_path, limit)
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
        path: &str,
        key: &str,
        size: u64,
        mtime_ns: u64,
        ignore_mtime: bool,
    ) -> PyResult<Option<Bound<'py, PyBytes>>> {
        let bytes_opt = self
            .engine
            .get(path, key, size, mtime_ns, ignore_mtime)
            .map_err(PyValueError::new_err)?;
        match bytes_opt {
            Some(b) => Ok(Some(PyBytes::new_bound(py, &b))),
            None => Ok(None),
        }
    }

    pub fn put(&self, path: &str, size: u64, mtime_ns: u64, key: &str, value: &Bound<'_, PyBytes>) -> PyResult<()> {
        self.engine
            .put(path, size, mtime_ns, key, value.as_bytes())
            .map_err(PyValueError::new_err)
    }

    #[pyo3(signature = (search=None, limit=20, offset=0))]
    pub fn get_cache_viewer_files<'py>(
        &self,
        py: Python<'py>,
        search: Option<&str>,
        limit: usize,
        offset: usize,
    ) -> PyResult<(usize, Vec<Bound<'py, PyDict>>)> {
        let (total, files) = self
            .engine
            .get_cache_viewer_files(search, limit, offset)
            .map_err(PyValueError::new_err)?;
        let mut py_files = Vec::with_capacity(files.len());
        for f in files {
            py_files.push(file_metadata_to_dict(py, &f)?);
        }
        Ok((total, py_files))
    }
}

#[pymodule]
fn dupeguru_rust(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<RustFilesDB>()?;
    Ok(())
}
