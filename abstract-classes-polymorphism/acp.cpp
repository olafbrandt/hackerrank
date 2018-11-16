#include <iostream>
#include <vector>
#include <map>
#include <string>
#include <algorithm>
#include <set>
#include <cassert>
using namespace std;

struct Node{
   Node* next;
   Node* prev;
   int value;
   int key;
   Node(Node* p, Node* n, int k, int val):prev(p),next(n),key(k),value(val){};
   Node(int k, int val):prev(NULL),next(NULL),key(k),value(val){};
};

class Cache{
   
   protected: 
   map<int,Node*> mp; //map the key to the node in the linked list
   int cp;  //capacity
   Node* tail; // double linked list tail pointer
   Node* head; // double linked list head pointer
   virtual void set(int, int) = 0; //set function
   virtual int get(int) = 0; //get function

};

class LRUCache : public Cache
{
    public:
    LRUCache (int cp)
    {
        this->cp = cp;
        this->head = NULL;
        this->tail = NULL;
    }
    
    virtual void set(int k, int v)
    {
        Node* pNode;
        map<int,Node*>::iterator it;

        // cerr << "set(" << k << "," << v << ") size:" << this->mp.size() << endl;

        pNode = NULL;
        it = this->mp.find(k);
        if (it != this->mp.end())
        {
            pNode = it->second;
            touch_node(pNode);
        }
        else
        {
            pNode = new Node(k, v);
            this->insert_node(pNode);
        }
        pNode->value = v;
        // dump_lru();
    }
    
    virtual int get(int k)
    {
        Node* pNode;
        map<int,Node*>::iterator it;

        // cerr << "get(" << k << ") size:" << this->mp.size() << endl;

        pNode = NULL;
        it = this->mp.find(k);
        if (it != this->mp.end())
        {
            pNode = it->second;
            touch_node(pNode);
            //dump_lru();
            return (pNode->value);
        }
        // dump_lru();
        return (-1);
    }

    void touch_node(Node* pNode)
    {
        //cerr << "touch_node(" << pNode->key << "," << pNode->value << ") size:" << this->mp.size() << endl;

        if (pNode != this->head)
        {
            snip_node(pNode);
            insert_node(pNode);
        }
    }
    
    void insert_node(Node* pNode)
    {
        Node** ppPrev;
        Node** ppNext;

        //cerr << "insert_node(" << pNode->key << "," << pNode->value << ") size:" << this->mp.size() << endl;
        
        if (this->mp.size() >= this->cp)
        {
            Node* pNode = this->tail;
            snip_node(this->tail);
            delete pNode;
            pNode = NULL;
        }
        
        ppPrev = &this->head;
        ppNext = (this->tail ? &this->head->prev : &this->tail);
        
        pNode->next = this->head;
        pNode->prev = NULL;
        *ppPrev = pNode;
        *ppNext = pNode;
        
        this->mp[pNode->key] = pNode;
        assert (this->mp.size() <= this->cp);
    }

    void snip_node(Node* pNode)
    {
        Node** ppPrev;
        Node** ppNext;

        //cerr << "snip_node(" << pNode->key << "," << pNode->value << ") size:" << this->mp.size() << endl;

        ppPrev = (pNode->prev ? &pNode->prev->next : &this->head);
        ppNext = (pNode->next ? &pNode->next->prev : &this->tail);

        *ppPrev = pNode->next;
        pNode->next = NULL;
        
        *ppNext = pNode->prev;
        pNode->prev = NULL;

        assert (this->mp.erase(pNode->key) == 1);
        assert (this->mp.size() <= this->cp);
    }
    
    void dump_lru()
    {
        Node* pNode;
        
        pNode = this->head;
        
        cerr << "LRU: ";
        while (pNode)
        {
            cerr << "(" << pNode->key << "," << pNode->value << ")";
            if (pNode->next)
            {
                cerr << ", ";
            }
            pNode = pNode->next;
        }
        cerr << endl;
    }
};

int main() {
   int n, capacity,i;
   cin >> n >> capacity;
   LRUCache l(capacity);
   for(i=0;i<n;i++) {
      string command;
      cin >> command;
      if(command == "get") {
         int key;
         cin >> key;
         cout << l.get(key) << endl;
      } 
      else if(command == "set") {
         int key, value;
         cin >> key >> value;
         l.set(key,value);
      }
   }
   return 0;
}
