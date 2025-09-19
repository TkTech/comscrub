/* header block */
// Single-line header comment

int main() {
    int x = 1; // initialize x
    /* block comment in cpp */
    int y = x/**/y; // ensure tokens don't merge
    const char* s = "/* not a comment */"; // string must remain
    return y; /* trailing */
}

