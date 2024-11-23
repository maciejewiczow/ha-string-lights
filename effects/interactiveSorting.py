def heapSort(arr, onUpdate):
    def heapify(arr, n, i):
        largest = i
        l = 2 * i + 1
        r = 2 * i + 2

        if l < n and arr[i] < arr[l]:
            largest = l

        if r < n and arr[largest] < arr[r]:
            largest = r

        if largest != i:
            arr[i],arr[largest] = arr[largest],arr[i]
            onUpdate()

            heapify(arr, n, largest)

    n = len(arr)

    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)

    for i in range(n-1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        onUpdate()
        heapify(arr, i, 0)


def mergeSort(myList, onListUpdate):
    if len(myList) > 1:
        mid = len(myList) // 2
        left = myList[:mid]
        right = myList[mid:]

        # Recursive call on each half
        mergeSort(left, onListUpdate)
        mergeSort(right, onListUpdate)

        # Two iterators for traversing the two halves
        i = 0
        j = 0

        # Iterator for the main list
        k = 0

        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
              # The value from the left half has been used
              myList[k] = left[i]
              onListUpdate()
              # Move the iterator forward
              i += 1
            else:
                myList[k] = right[j]
                onListUpdate()
                j += 1
            # Move to the next slot
            k += 1

        # For all the remaining values
        while i < len(left):
            myList[k] = left[i]
            onListUpdate()
            i += 1
            k += 1

        while j < len(right):
            myList[k]=right[j]
            onListUpdate()
            j += 1
            k += 1

def bubbleSort(arr, onUpdate):
    n = len(arr)

    for i in range(n-1):
        for j in range(0, n-i-1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                onUpdate()
