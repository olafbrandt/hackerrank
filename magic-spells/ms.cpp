#include <iostream>
#include <vector>
#include <string>
using namespace std;

class Spell { 
    private:
        string scrollName;
    public:
        Spell(): scrollName("") { }
        Spell(string name): scrollName(name) { }
        virtual ~Spell() { }
        string revealScrollName() {
            return scrollName;
        }
};

class Fireball : public Spell { 
    private: int power;
    public:
        Fireball(int power): power(power) { }
        void revealFirepower(){
            cout << "Fireball: " << power << endl;
        }
};

class Frostbite : public Spell {
    private: int power;
    public:
        Frostbite(int power): power(power) { }
        void revealFrostpower(){
            cout << "Frostbite: " << power << endl;
        }
};

class Thunderstorm : public Spell { 
    private: int power;
    public:
        Thunderstorm(int power): power(power) { }
        void revealThunderpower(){
            cout << "Thunderstorm: " << power << endl;
        }
};

class Waterbolt : public Spell { 
    private: int power;
    public:
        Waterbolt(int power): power(power) { }
        void revealWaterpower(){
            cout << "Waterbolt: " << power << endl;
        }
};

class SpellJournal {
    public:
        static string journal;
        static string read() {
            return journal;
        }
}; 
string SpellJournal::journal = "";

void counterspell(Spell *spell) {
    if (Fireball* sf = dynamic_cast<Fireball*>(spell)) {
      sf->revealFirepower();
    }
    else if (Frostbite* sf = dynamic_cast<Frostbite*>(spell)) {
      sf->revealFrostpower();
    }
    else if (Thunderstorm* sf = dynamic_cast<Thunderstorm*>(spell)) {
      sf->revealThunderpower();
    }
    else if (Waterbolt* sf = dynamic_cast<Waterbolt*>(spell)) {
      sf->revealWaterpower();
    }
    else {
        int i, j;
        string sn = spell->revealScrollName();
        string sj = SpellJournal::read();
        int m = sn.length()+1;
        int n = sj.length()+1;

        vector<vector<int> > c(m);
        for (i = 0 ; i < m ; i++)
            c[i].resize(n);

        for (i = 1; i < m; i++) {
            for (j = 1; j < n; j++) {
                if (sn.c_str()[i-1] == sj.c_str()[j-1])
                    c[i][j] = c[i-1][j-1] + 1;
                else
                    c[i][j] = max(c[i][j-1], c[i-1][j]);
            }
        }

        cout << c[m-1][n-1] << endl;
    }

}

class Wizard {
    public:
        Spell *cast() {
            Spell *spell;
            string s; cin >> s;
            int power; cin >> power;
            if(s == "fire") {
                spell = new Fireball(power);
            }
            else if(s == "frost") {
                spell = new Frostbite(power);
            }
            else if(s == "water") {
                spell = new Waterbolt(power);
            }
            else if(s == "thunder") {
                spell = new Thunderstorm(power);
            } 
            else {
                spell = new Spell(s);
                cin >> SpellJournal::journal;
            }
            return spell;
        }
};

int main() {
    int T;
    cin >> T;
    Wizard Arawn;
    while(T--) {
        Spell *spell = Arawn.cast();
        counterspell(spell);
    }
    return 0;
}
