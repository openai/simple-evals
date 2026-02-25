# array-move

> Move an array item to a different position

## Install

```
$ npm install array-move
```

## Usage

```js
import {arrayMoveImmutable} from 'array-move';

const input = ['a', 'b', 'c'];

const array1 = arrayMoveImmutable(input, 1, 2);
console.log(array1);
//=> ['a', 'c', 'b']

const array2 = arrayMoveImmutable(input, -1, 0);
console.log(array2);
//=> ['c', 'a', 'b']

const array3 = arrayMoveImmutable(input, -2, -3);
console.log(array3);
//=> ['b', 'a', 'c']
```

## API

### arrayMoveImmutable(array, fromIndex, toIndex)

Clones the given `array`, moves the item to a new position in the new array, and then returns the new array. The given `array` is not mutated.

### arrayMoveMutable(array, fromIndex, toIndex)

Moves the item to the new position in the `array` array. Useful for huge arrays where absolute performance is needed.

#### array

Type: `Array`

#### fromIndex

Type: `number`

The index of item to move.

If negative, it will begin that many elements from the end.

#### toIndex

Type: `number`

The index of where to move the item.

If negative, it will begin that many elements from the end.
