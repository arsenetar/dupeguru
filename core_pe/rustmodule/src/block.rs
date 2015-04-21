#![feature(libc)]
extern crate libc;
extern crate image;
use libc::c_char;
use std::ffi::CStr;
use std::str;
use std::path::Path;
use image::GenericImage;

#[no_mangle]
pub extern "C" fn block(value: *const c_char) -> u32 {
    let slice = unsafe { CStr::from_ptr(value) };
    let path = &Path::new(str::from_utf8(slice.to_bytes()).unwrap());
    let image = image::open(path).unwrap().to_rgb();
    let mut totr: u32 = 0;
    let mut totg: u32 = 0;
    let mut totb: u32 = 0;
    for pixel in image.pixels() {
        let data = pixel.data;
        totr += data[0] as u32;
        totg += data[1] as u32;
        totb += data[2] as u32;
    }
    println!("foo! {} {} {}", totr, totg, totb);
    42
}

