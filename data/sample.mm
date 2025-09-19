/* objc++ header */
// Obj-C++ single-line

int main() {
    int m = 1; // initialize m
    /* objc++ block comment */
    int n = m/**/n; // ensure tokens don't merge
    const char* s = "/* not a comment */"; // string must remain
    return n; /* trailing */
}

