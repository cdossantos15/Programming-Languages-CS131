let accept_all string = Some string
let accept_empty_suffix = function
   | _::_ -> None
   | x -> Some x

type english_nonterminals =
  | S | NP | VP | A | Nn | PN | V


  let english_grammar =
  (S,
   function
     | S ->
         [[N NP; N VP]]
     | NP ->
	 [[N A; N Nn];
	  [N PN]]
     | VP ->
	 [[ N V]; [N V; N NP]]
     | A ->
	 [[T"a"];
	  [T"the"]]
     | Nn ->
	 [[T"cat"];
	  [T"food"]; [T "book"]]
     | PN ->
	 [[T"UCLA"]; [T"James"]; [T"LA"]; [T"Claudia"]]
	 | V -> [[T "reads"]; [T "plays"]; [T "is"]]
	  )

  let small_english_frag = ["$"; "1"; "++"; "-"; "2"]

let make_matcher_test =
  ((make_matcher english_grammar accept_all ["Claudia"; "sees"; "a"; "cat"; "the";
"book"; "is"; "a"]) = None)


