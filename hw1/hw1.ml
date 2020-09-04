type ('nonterminal, 'terminal) symbol =
  | N of 'nonterminal
  | T of 'terminal

let rec find x l =
match l with 
|[] -> false (*if list is empty, not found*)
|hd::tl -> if hd = x then true else find x tl (*if the first element is ~x, recursivley check the rest in the list*)
;;

let rec subset a b =
match a with
| [] -> true (* empty set is a subset, so true*)
| hd::tl -> if not (find hd b) then false else (subset tl b)
(* split list into head and tail. If the head is not found in tail, then
it is not a subset, else call subset on the rest of elements*)
;;

let rec equal_sets a b = 
  subset a b && subset b a
;; (* if both lists are subsets of each other then they are equal*)

let set_union a b = a @ b;; (* combine lists to form union *)

let rec set_intersection a b =
match a with
|[] -> [] (* if a is empty, lists have nothing in common *)
|hd::tl -> if find hd b then hd::(set_intersection tl b)
else set_intersection tl b;;
(* if hd is in b, then construct list that includes head, if not try to
find intersection with the rest of the list *)

let rec set_diff a b =
match a with
| [] -> []
| x::r -> if not (find x b) then x::(set_diff r b)
else set_diff r b;;

let rec computed_fixed_point eq f x = 
if eq x (f x) then x (* if x=f(x), fixed pt = x *)
else computed_fixed_point eq f (f x);;
(* recursively find f(f(x))..etc until you find fixed pt *)

(*FILTER_REACHABLE HELPER FUNCTIONS*)

(* reach_helper:
	- returns nonterminals from one rule *)
let rec reach_helper s r =
match r with
| [] -> []
| (N nt)::tl -> if not (find nt s) then nt::(reach_helper (nt::s) tl)
		else (reach_helper s tl)
| (_)::tl -> reach_helper s tl ;;


(* reach_from:
	- returns reachable NTs from the NT specified *) 
let rec reach_from nt s r =
match r with
| [] -> []
| (lhs, a)::tl -> if (lhs = nt) then (reach_helper s a)@(reach_from nt ((reach_helper s a)@s) tl)
else (reach_from nt s tl)
;;

(* get_nts:
	- returns list of all reachable nonterminals *)
let rec get_nts nts s r =
match nts with
| [] -> []
| hd::tl -> hd:: (get_nts (reach_from hd (nts@s) r ) (nts@s) r)@(get_nts tl (nts@s) r) ;;

(* is_valid:
	- returns true if rule is valid *)
let is_valid rule nts = 
match rule with
| (sym, _) -> if (find sym nts) then true else false;;

let get_start g =
match g with
| (sym, _) -> sym;;

let get_rules g =
match g with
| (_,rules) -> rules;;

let rec reachable_rules nt_list rules = 
match rules with
| [] -> []
| hd::tl -> if (is_valid hd nt_list) then hd::(reachable_rules nt_list tl)
		else (reachable_rules nt_list tl);;

let filter_reachable g = 
(get_start g), (reachable_rules (get_nts [(get_start g)] [] (get_rules g) ) (get_rules g));; 
