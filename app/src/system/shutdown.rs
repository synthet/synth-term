//! Detection of an OS-initiated end of the desktop session (shutdown, restart, or logout).
//!
//! When Windows ends the session it kills every console process, so each shell exits and, left
//! alone, closes its pane and tab and rewrites the session snapshot without it, leaving little or
//! nothing to restore (warpdotdev/warp#15269). Knowing that the OS started the teardown lets us keep
//! the panes and the snapshot as they were.

use std::sync::atomic::{AtomicBool, Ordering};

static SESSION_ENDING: AtomicBool = AtomicBool::new(false);

/// Records that the OS asked the app to quit as part of ending the session.
///
/// Latched for the rest of the process: approving a system-initiated termination commits the app to
/// quitting.
pub fn note_session_ending() {
    if !SESSION_ENDING.swap(true, Ordering::SeqCst) {
        log::info!("OS session is ending; keeping open tabs intact for session restore");
    }
}

/// Returns whether the OS is ending the session (shutdown, restart, or logout).
pub fn is_session_ending() -> bool {
    SESSION_ENDING.load(Ordering::SeqCst) || platform_is_session_ending()
}

#[cfg(windows)]
fn platform_is_session_ending() -> bool {
    use windows::Win32::UI::WindowsAndMessaging::{GetSystemMetrics, SM_SHUTTINGDOWN};

    // Queried each time rather than latched because Windows clears it again if the shutdown is
    // aborted, and normal behaviour should come back when that happens.
    unsafe { GetSystemMetrics(SM_SHUTTINGDOWN) != 0 }
}

#[cfg(not(windows))]
fn platform_is_session_ending() -> bool {
    false
}

#[cfg(test)]
#[path = "shutdown_tests.rs"]
mod tests;
