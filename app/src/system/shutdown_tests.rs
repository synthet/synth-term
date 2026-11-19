use super::*;

// Latches a process-global flag, so this is the only test that touches it.
#[test]
fn note_session_ending_latches() {
    assert!(!is_session_ending());

    note_session_ending();
    assert!(is_session_ending());

    note_session_ending();
    assert!(is_session_ending());
}
