#include <iostream>

using namespace std;

int main()
{
    auto func = [] () { cout << "Hello world" << endl; };
    func(); // now call the function
}
