#include <iostream>
#include <deque> 
#include <set>
#include <assert.h>

using namespace std;
void printKMax2(int arr[], int n, int k){
    deque<int> dq;
    multiset<int> ms;
    
    for (int i = 0; i < k; i++) {
        //cerr << "ins: " << arr[i] << endl;
        ms.insert(arr[i]);
    }
    cout << *ms.rbegin() << " ";
    for (int i = k; i < n; i++) {
        //assert (ms.erase(arr[i - k]) == 1);
        ms.erase(ms.find(arr[i - k]));
        ms.insert(arr[i]);
        //cerr << "erase: " << arr[i - k] << ", ins: " << arr[i] << endl;
        cout << *ms.rbegin() << " ";
    }
    cout << endl;
}

// A Dequeue (Double ended queue) based method for printing maixmum element of
// all subarrays of size k
void printKMax(int arr[], int n, int k)
{
    // Create a Double Ended Queue, Qi that will store indexes of array elements
    // The queue will store indexes of useful elements in every window and it will
    // maintain decreasing order of values from front to rear in Qi, i.e., 
    // arr[Qi.front[]] to arr[Qi.rear()] are sorted in decreasing order
    std::deque<int>  Qi(k);

    /* Process first k (or first window) elements of array */
    int i;
    for (i = 0; i < k; ++i)
    {
        // For very element, the previous smaller elements are useless so
        // remove them from Qi
        while ( (!Qi.empty()) && arr[i] >= arr[Qi.back()])
            Qi.pop_back();  // Remove from rear

        // Add new element at rear of queue
        Qi.push_back(i);
    }

    // Process rest of the elements, i.e., from arr[k] to arr[n-1]
    for ( ; i < n; ++i)
    {
        // The element at the front of the queue is the largest element of
        // previous window, so print it
        cout << arr[Qi.front()] << " ";

        // Remove the elements which are out of this window
        while ( (!Qi.empty()) && Qi.front() <= i - k)
            Qi.pop_front();  // Remove from front of queue

        // Remove all elements smaller than the currently
        // being added element (remove useless elements)
        while ( (!Qi.empty()) && arr[i] >= arr[Qi.back()])
            Qi.pop_back();

         // Add current element at the rear of Qi
        Qi.push_back(i);
    }

    // Print the maximum element of last window
    cout << arr[Qi.front()];

    cout << endl;
}

int main(){
  
   int t;
   cin >> t;
   while(t>0) {
      int n,k;
       cin >> n >> k;
       int i;
       int arr[n];
       for(i=0;i<n;i++)
            cin >> arr[i];
       printKMax2(arr, n, k);
       t--;
     }
     return 0;
}

