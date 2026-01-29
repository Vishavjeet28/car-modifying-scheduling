## 2024-05-22 - Missing Skip-to-Content Link
**Learning:** This app relies heavily on a fixed top navbar with many links, making it difficult for keyboard users to reach the main content quickly.
**Action:** Implemented a standard "Skip to main content" link using Bootstrap's `visually-hidden-focusable` class and custom CSS for positioning over the fixed header. Always check for fixed headers when implementing skip links.
