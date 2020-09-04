let my_equal_sets_test0 = equal_sets [1;2] [1;2] 
let my_subset_test0 = subset [1;2] [1;2;3;4]
let my_set_union_test1 = equal_sets (set_union [1] []) [1];;

let my_set_intersection_test0 = equal_sets (set_intersection [1;2] []) [];;

let my_set_diff_test0 = equal_sets (set_diff [1;2] [1;4;2;1]) []

let my_computed_fixed_point_test0 = computed_fixed_point (=) (fun x -> x) 1;;

type my_fruits = 
| Apple | Banana | Pear | Kiwi

let fruit_salad = 
Apple, [ Apple, [T"a"; N Banana];
	 Apple, [N Kiwi];
	Banana, [T"b"; N Apple];
	Pear, [N Banana];
	Kiwi, [T"k"; N Banana]
]

let my_filter_reachable_test0 = 
filter_reachable fruit_salad = (Apple, [ Apple, [T"a"; N Banana];
         Apple, [N Kiwi];
        Banana, [T"b"; N Apple];
        Kiwi, [T"k"; N Banana]]);;
