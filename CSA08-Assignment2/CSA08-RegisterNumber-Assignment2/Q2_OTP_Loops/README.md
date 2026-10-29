# Q2 – OTP Verification Loops

Run: `python q2_otp.py`

The program demonstrates both a `while` loop and a `for range(3)` loop. A blank OTP uses `continue` and does not consume an attempt. A correct OTP uses `break`. `pass` is shown as a placeholder for a future audit action. The loop `else` block locks the account when all allowed attempts finish without a successful OTP.

For the changed condition, a correct security answer increases the maximum attempts from three to five.

**Complexity:** For a attempts, time is O(a). A loop uses O(1) extra space. A recursive version would use O(a) call-stack space.
