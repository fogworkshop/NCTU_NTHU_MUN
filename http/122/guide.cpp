#include <iostream>
#include <vector>
#include <map>//map<string, info> cls;`
#include <set> //set<string> exist;
#include <cstdio>
using namespace std;
class info//cls[name]
{
public:
	vector<string> pblc, prtc, prvt;// cls[name].pblc[i]
	string inhe;//cls[name].inhe
	int inhetype;//none == 0, public == 2, protected == 3, private == 4
	void print(string name){
		cout << "name : " << name << endl;
		cout << "inhe : " << inhe << endl;
		cout << "inhetype : ";
		if(inhetype == 0) cout << "none" << endl;
		else if (inhetype == 1) cout << "public" << endl;
		else if (inhetype == 2) cout << "protected" << endl;
		else if (inhetype == 3) cout << "private" << endl;
		cout << "public : ";
		for(size_t i = 0; i < pblc.size(); i++){
			cout << pblc[i] << ' ';
		} 
		cout << endl;
		cout << "protected : ";
		for(size_t i = 0; i < prtc.size(); i++){
			cout << prtc[i] << ' ' ;
		}
		cout << endl;
		cout << "private : ";
		for(size_t i = 0; i < prvt.size(); i++){
			cout << prvt[i] << ' ';
		}
		cout << endl;
	}
};
void solve(string from, string acscls, string acsmem, map<string, info> cls, map<int, string> inhetypemap, set<string> exist, set<string> clsexist){
	if(exist.count(acsmem) == 0){//not found
		cout << "Member not found" << endl;
		return ;
	}
	else if (clsexist.count(acscls) == 0){
		cout << "Class not found" << endl;
		return ;
	}
/*	
	else if (from != acscls){
		for (size_t i = 0; i < cls[acscls].pblc.size(); i++){
			if(acsmem == cls[acscls].pblc[i]){
				cout << acscls << '.' << acsmem << endl;
				return ;
			}
		}
		cout << "Invalid access" << endl;
		return ;
	}	
*/
	else {
		int state = 0, oristate = 0;//public = 4; protected = 3; private = 2; hidden = 1;
		vector<string> check;
		bool isfound = 0;
		string iacscls = acscls;
		for(; cls[iacscls].inhetype != 0 && isfound == 0;  iacscls = cls[iacscls].inhe){
			for(size_t i = 0; i < cls[iacscls].pblc.size() && isfound == 0; i++){
				if(acsmem == cls[iacscls].pblc[i]){
					check.push_back(iacscls);
//					cout << "pushing " << iacscls << endl;
					state = 4;//state : public = 4;
					isfound = 1;
				}
			}
			for(size_t i = 0; i < cls[iacscls].prtc.size() && isfound == 0; i++){
				if(acsmem == cls[iacscls].prtc[i]){
					check.push_back(iacscls);
//					cout << "pushing " << iacscls << endl;
					state = 3;//state protected = 3;
					isfound = 1;
				}			
			}
			for(size_t i = 0; i < cls[iacscls].prvt.size() && isfound == 0; i++){
				if(acsmem == cls[iacscls].prvt[i]){
					check.push_back(iacscls);
//					cout << "pushing " << iacscls << endl;
					state = 2;//state private = 2;
					isfound = 1;
				}
			}
			if(isfound == 0){
			check.push_back(iacscls);
//			cout << "pushing.. " << iacscls << endl;
			check.push_back(inhetypemap[cls[iacscls].inhetype]);
//			cout << "pushing " << inhetypemap[cls[iacscls].inhetype] << endl;
			}

		}
		if (isfound == 0){
			for(size_t i = 0; i < cls[iacscls].pblc.size() && isfound == 0; i++){
				if(acsmem == cls[iacscls].pblc[i]){
					check.push_back(iacscls);
//					cout << "pushing2 " << iacscls << endl;

					state = 4;
					isfound = 1;
				}
			}
			for(size_t i = 0; i < cls[iacscls].prtc.size() && isfound == 0; i++){
				if(acsmem == cls[iacscls].prtc[i]){
					check.push_back(iacscls);
//					cout << "pushing2 " << iacscls << endl;
					state = 3;
					isfound = 1;
				}			
			}
			for(size_t i = 0; i < cls[iacscls].prvt.size() && isfound == 0; i++){
				if(acsmem == cls[iacscls].prvt[i]){
					check.push_back(iacscls);
//					cout << "pushing2 " << iacscls << endl;
					state = 2;
					isfound = 1;
				}
			}
		}
//output
		
/*
//		cout << "*************************" << endl;
//		cout << "isfound" << isfound << endl;
		cout << "check: " ;
		for(size_t i = 0; i < check.size(); i++){
			cout << check[i] << ' ' ;
		} 
		cout << endl;
//		cout << "*************" << endl;
*/
//outputend
		oristate = state;
		if(isfound == 0){
			cout << "Member not found" << endl;
		}
		//判斷state
		else if (isfound == 1){			
			string fromcls = check.back();
//			int tmpstate = 0;
			bool isfather = false;
			bool allispub = true;
			if(check.back() == from && check.size() > 1){
				isfather = true;
			}

			
//output
//			cout << "from : " << fromcls << endl;
//			cout << "oristate : " << oristate << endl;
//outputend
			map<string, int> tmpstatemap;
			string tmpname = check.back();
			tmpstatemap[check.back()] = state;
			for (;check.size() > 1 /*&& state > 1*/;){
//				cout << "poping " << check.back() << endl;

				check.pop_back();


				if(check.back() == "protected" || check.back() == "private"){
					allispub = false;
				}
//output

//		cout << "*************************" << endl;
//		cout << "isfound" << isfound << endl;
//		for(size_t i = 0; i < check.size(); i++){
//			cout << check[i] << ' ' ;
//		} 
//		cout << endl;
		
//		cout << "*************" << endl;
//outputend		
				if(check.back() == from &&check.size() > 1){
					isfather = true;
	//				tmpstate = state;
				}

				if(check.back() == "public"){
					if(state == 2){//only private changes
						state = 1;
					}
				}
				else if (check.back() == "protected"){
					if(state == 4){
						state = 3;
					}
					else if (state == 3){
						continue;
					}			
					else if (state == 2){
						state = 1;
					}			
				}
				else if ( check.back() == "private"){
					if(state > 2){
						state = 2;
					}
					else if ( state == 2){
						state = 1;
					}
				}
				tmpstatemap[tmpname] = state;
				if(check.back() != "public" && check.back() != "protected" && check.back() != "private"){
					tmpname = check.back();
				}
			}
			vector<string> tmpcheck(check);

		//判斷
			if(from != acscls){
				if (isfather == false){//外人
//output
	//				cout << "isoutsider" << endl;
	//				cout  << "notfather" << endl; 
					if(state == 4){
						cout << fromcls << '.' << acsmem << endl;
					}
					else{
						cout << "Invalid access" << endl;
					}
				}
				else if (isfather == true){//from是acscls祖先(A B.a)
	//outputene
//					cout << " haha" << endl;
					if(allispub == true){
						if(oristate > 1){
						cout << fromcls << '.' << acsmem << endl;
						}
						else {
							cout << "Invalid access" << endl;                
						}
					}
					else if(allispub == false) {
						if(oristate == 4){
							cout << fromcls << '.' << acsmem << endl;
						}
						else{
						cout << "Invalid access" << endl;
						}
					}				
				}
			}

			else if (from == acscls){
				if(state > 1){
					cout << fromcls << '.' << acsmem << endl;
					return ;
				}
				else if (state == 1){
					cout << "Invalid access" << endl;
					return ;
				}
			}
		}
	}
	return ;
}

int main()
{	
	set<string> clsexist;
	set<string> exist;
	map<int, string> inhetypemap;
	inhetypemap[0] = "none";
	inhetypemap[1] = "public";
	inhetypemap[2] = "protected";
	inhetypemap[3] = "private";
	int n; cin >> n;
	map<string, info> cls;
	while(n--){
		int cls_or_stru = 0;
		string type, name, column;
		cin >> type >> name >> column;
		clsexist.insert(name);
		if(type == "class") cls_or_stru = 1;
		else if (type == "struct") cls_or_stru = 2;
		string inhetype; cin >> inhetype;
		if(inhetype == "none"){
			cls[name].inhetype = 0;
		}
		else if (inhetype == "public"){
			cls[name].inhetype = 1;
			cin >> cls[name].inhe;
		}
		else if (inhetype == "protected"){
			cls[name].inhetype = 2;
			cin >> cls[name].inhe;
		}
		else if (inhetype == "private"){
			cls[name].inhetype = 3;
			cin >> cls[name].inhe;
		}
		else{ // default
			if(cls_or_stru == 1){
				cls[name].inhetype = 3;
				string name_ = inhetype;
				cls[name].inhe = name_;
			}
			else if (cls_or_stru == 2){
				cls[name].inhetype = 1;
				string name_ = inhetype;
				cls[name].inhe = name_;
			}
		}
		
		
		string memtype, mem;
		while(cin >> memtype, memtype != "end"){
			cin >> mem;
			if(memtype == "public"){
				cls[name].pblc.push_back(mem);
				exist.insert(mem);
			}
			else if (memtype == "protected"){
				cls[name].prtc.push_back(mem);
				exist.insert(mem);
			}
			else if (memtype == "private"){
				cls[name].prvt.push_back(mem);
				exist.insert(mem);
			}
		}	
//output
/*		
					cout << endl;
					cout << "..............." << endl;
					cls[name].print(name);
					cout << "..............." << endl;
*/
//outputend
	}
	string from;
	while(cin >> from){
		string acscls, acsmem;
		while(cin.peek() == ' ' || cin.peek() == '\n')
			getchar();

		char ch;
		while(ch = getchar(), ch !='.')
			acscls.push_back(ch);

		cin >> acsmem;
		solve(from, acscls, acsmem, cls, inhetypemap, exist, clsexist);
	}
	return 0;
}
