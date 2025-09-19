/* objc header */
// Obj-C single-line

int main() {
    int a = 1; // initialize a
    /* objc block comment */
    int b = a/**/b; // ensure tokens don't merge
    const char* s = "/* not a comment */"; // string must remain
    return b; /* trailing */
}

