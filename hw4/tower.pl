/* Tests:
plain_tower(5,
         [[2,3,4,5,1],
          [5,4,1,3,2],
          [4,1,5,2,3],
          [1,2,3,4,5],
          [3,5,2,1,4]],
         C).
tower(5, T,
         counts([2,3,2,1,4],
                [3,1,3,3,2],
                [4,1,2,5,2],
                [2,4,2,1,2])).

*/                
/* set the values to be 1-N for all elements of T */
set_values(_, []).
set_values(N, [H | T]) :- fd_domain(H, 1, N), set_values(N, T).

/* checks to see if all the elements in T have N numbers*/
t_elem_len(_, []).
t_elem_len(N, [H | T]) :- length(H, N), t_elem_len(N, T).

rev_rows([], []).
rev_rows([T | Ts], [Tr | Trs]) :- reverse(T, Tr), rev_rows(Ts, Trs).

/* turn rows into cols, using prolog's implementation */
transpose([], []).
transpose([L | Ls], Ts) :- transpose_(L, [L | Ls], Ts).
transpose_([], _, []).
transpose_([_ | Es], Lists0, [Fs | Fss]) :-
	maplist(list_first_rest, Lists0, Fs, Lists),
	transpose_(Es, Lists, Fss).
list_first_rest([L | Ls], L, Ls).

counter([H | Tl], Co) :- counter(Tl, H, 1, Co).
counter([], _, C, C).
counter([H | Tl], M, C, Co) :- H > M, C1 is C+1, counter(Tl, H, C1, Co).
counter([H | Tl], M, C, Co) :- H < M, counter(Tl, M, C, Co).

/* verify the counter */
verify([], []).
verify([[H | Tl] | T], [C | Ct]) :- counter([H | Tl], C), verify(T, Ct).

values(N, D) :- findall(X, between(1, N, X), D).

solve([], _).
solve([H | Tl], N) :- values(N, D), permutation(D, H), solve(Tl, N).
diff(L) :- sort(L, S), length(L, L1), length(S, L2), L1 == L2.

/*
Check all the constraints for the tower:
-len of rows should be N
- each list in T should be len N
- All nums in rows of T must be from 1-N
- row nums are different
- col nums are different
*/
tower(N, T, C) :-
length(T, N),
t_elem_len(N, T),
set_values(N, T),
maplist(fd_all_different, T),
transpose(T, Cols),
maplist(fd_all_different, Cols), maplist(fd_labeling, T),
rev_rows(T, Tl), rev_rows(Cols, RCols),
counts(Top, Bot, Left, Right) = C,
length(Top, N), length(Bot, N), length(Left, N), length(Right, N),
verify(Cols, Top), verify(RCols, Bot), verify(T, Left), verify(Tl, Right).

plain_tower(N, T, C) :-
length(T, N),
t_elem_len(N, T),
solve(T, N),	
transpose(T, Cols),
maplist(diff, Cols),
rev_rows(T, Tl), rev_rows(Cols, ColsR),
counts(Top, Bot, Left, Right) = C,
length(Top, N), length(Bot, N), length(Left, N), length(Right, N),
verify(Cols, Top), verify(ColsR, Bot), verify(T, Left), verify(Tl, Right).


speedup(Ratio) :-
statistics(cpu_time, [_, _]), tower(4, Tower1, C),
statistics(cpu_time, [_ , E1]), plain_tower(4, Tower2, C),
statistics(cpu_time, [_ , E2]),
Plaintower is 1.0*(E2+1), Tow is 1.0*(E1+1),
write(E1), nl, write(E2), nl, Ratio is Plaintower/Tow.


ambiguous(N, C, T1, T2) :- tower(N, T1, C), tower(N, T2, C),
	T1 \= T2.