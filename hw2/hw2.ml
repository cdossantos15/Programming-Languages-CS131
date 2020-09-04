
type ('nonterminal, 'terminal) symbol =
  | N of 'nonterminal
  | T of 'terminal

type ('nonterminal, 'terminal) parse_tree =
  | Node of 'nonterminal * ('nonterminal, 'terminal) parse_tree list
  | Leaf of 'terminal


(* CONVERT_RULES
- need to pass in nt that has already been logged
- pass in the list of rules

Checks to see if the lhs has already been accounted for.
If it has, then add it to the  function.
If not, add it to a new function.
*)
let rec convert_rules nt rules =
	match rules with
	| [] -> []
	| (x, r)::tl ->
	if nt = x then r::(convert_rules nt tl)
else convert_rules nt tl


(* Returns first element of gram1 (start symbol)
gets the rest of the input (the rules), and converts
them by adding it to the function nt by calling "convert_rules". 
*)
let convert_grammar gram1 =
	(fst gram1), (fun nt -> (convert_rules nt (snd gram1)))


let rec parse_tree_leaves tree =
	match tree with
	| Leaf v -> [v]
	| Node (a, lhs::rhs) -> (parse_tree_leaves lhs)@(parse_tree_leaves (List.hd rhs))

(* test case:
parse_tree_leaves (Node ("*", [Leaf 1; (Node ("+", [Node("*", [Leaf 2; Leaf 3]); Leaf 4]))]))
*)

let rec match_or sym func rules accept deriv frag =
	match rules with
	| [] -> None
	| hd::tl -> match (match_and hd (func) accept (deriv@[sym, hd]) frag) with (*pass in the deriv appended deriv@hd *)
				| None -> (match_or sym (func) tl accept deriv frag)
				| answer -> answer (*success!*)
and match_and rule funk accept deriv frag =
	match rule with
	| [] -> accept deriv frag (*ran out of rules*)
	| hd::tl -> match frag with
				| [] -> None (*doesn't match *)
				| x::r -> match hd with
						| T t -> if x = t then (match_and tl (funk) accept deriv r) else None
						| N n -> (match_or n (funk) (funk n) (match_and tl (funk) accept) deriv frag)

let match_accept_wrap acceptor deriv frag = acceptor frag

let make_matcher gram accept frag =
	match gram with
	| (s, f) -> let acc = match_accept_wrap accept
in (match_or s f (f s) acc [] frag)


(*
make_parser: same format as make matcher except instead of wrapping accept function,

if it returns none, you weren't able to parse it. If it returns something (the derivation)
then you'd be able to make the tree

Some
 [
 (Expr, [N Term; N Binop; N Expr]);
 (Term, [N Lvalue; N Incrop]);
 (Lvalue, [T "$"; N Expr]);
(Expr, [N Term]);
(Term, [N Num]);
 (Num, [T "1"]);
(Incrop, [T "++"]);
(Binop, [T "-"]);
(Expr, [N Term]);
 (Term, [N Num]);
(Num, [T "2"])
]

*)
