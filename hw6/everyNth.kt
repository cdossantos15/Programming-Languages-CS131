fun main() {
    var test = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                     11, 12, 13, 14, 15, 16, 17, 18, 19, 20)
   if (everyNth(test, 0) == listOf<Any>())
   print("Test 0 SUCCESS\n")
   if (everyNth(test, 1) == listOf<Any>(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20))
   print("Test 1 SUCCESS\n")
   if (everyNth(test, 2) == listOf<Any>(2, 4, 6, 8, 10, 12, 14, 16, 18, 20))
   print("Test 2 SUCCESS\n")
   if (everyNth(test, 21) == listOf<Any>())
   print("Test 21 SUCCESS\n")

    
}

fun everyNth (list: List<Any>, n: Int): List<Any>{
    var newList = mutableListOf<Any>()
    if (n < 1) {
    return listOf<Any>()
    }
    for (i in 0..(list.size-1)) {
        if ( (i+1) % n == 0)
        newList.add(list.get(i))
    }
    return newList.toList()
}