// Leading line comment should be removed
#include <stdio.h> /* include is fine */

int main() {
    int x = 1; // initialize x
    /* block
       comment */
    int y = x/**/y; // ensure tokens don't merge
    printf("/* not a comment */\n"); // inside string must remain
    // URL http://example.com should be removed entirely
    return y; /* trailing */
}

