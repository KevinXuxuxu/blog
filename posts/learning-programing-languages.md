---
title: Learning Programing Languages
date: 2022-07-31 13:59:40
tags: ["Go", "Programing Language", "Functional Programing"]
category: tech
---
Lately I have been looking into some of the newly created programing languages as I'm getting bored with [_the ELden Ring_](https://en.wikipedia.org/wiki/Elden_Ring) and [_Risk of Rain 2_](https://en.wikipedia.org/wiki/Risk_of_Rain_2). My interest in programing languages started a few years ago when I found [Destroy All Software](https://www.destroyallsoftware.com/screencasts) and learned more about how to design and implement a programing language and its compiler, after which I wrote some toy compilers (e.g. [mini-c-compiler](https://github.com/KevinXuxuxu/mini_c_compiler), [pineapple-py](https://github.com/KevinXuxuxu/pineapple-py)). At the time I was not able to going forward partly because I feel like I'm not understanding some important concept behind the scene. Now I want to try to approach it in some different directions.

#### Functional Programing
I was also quite fascinated by the functional programing paradigm as I was checking out [the series of screencasts about computation](https://www.destroyallsoftware.com/screencasts/catalog/introduction-to-computation) on destroy all softwares. It's really amazing how lambda calculus could actually be as powerful in computing as traditional turing machine and Von Neumann architecture, while completely different from them in the first place.

Recently I learned about Monad, an important concept in the functional programing area. Simply speaking, it is a design pattern that wraps a set of additional and potentially complex logic, and abstracts it away from the main (business) logic, which makes the code much more readable and easier to maintain. One of the famous monads is the Option monad (or the Maybe monad). This monad abstracts the logic of handling absent values along the regular business logic, which is a very common thing you need to do when dealing with database operation or big data analysis. Using Option as an example, we can see how monad is composed:
- The type constructor _M_: the `Option[T]` type, which indicates that there might be an object of type `T` or nothing (`None`).
    - Note that this "monadic" type is also generic, which means it can hold any concrete (or "pure") type, but not all monadic types have to be generic.
- the _return_ operation: the `Some(T v)` method, which converts a pure object of type `T` into the "impure" type `Option[T]`.
- the _bind_ operation (`>>=`): the user defined logic which takes in a regular ("pure") operation and apply it to an impure input, handling the missing value logic on the way.

This paradigm not only helps handling missing value, it could also abstract the logic for generating and collecting logs, broadcasting operations on array, and basically any complex logic you want to handle alongside the real business logic.

But there is one thing that I want to solve with monad, but couldn't find a better way: the error handling logic in Go. Look at the following logic:

```Go
func fa(a int) (int, error) {
    // does something
    if (/* some condition */) {
        return nil, fmt.Errorf("something")
    }
    // does something else
    return sth, nil
}

func fb(b int) error {
    // does something
    if (/* some condition */) {
        return fmt.Errorf("something")
    }
    // does something else
    return nil
}

func fc(c int) error {
    fa_c, err := fa(c)
    if err != nil {
        return err
    }
    fa_fa_c, err := fa(fa_c)
    if err != nil {
        return err
    }
    if err = fb(fa_c); err != nil {
        return err
    }
    return nil
}
...
```

Note that the more levels of call stack in the codebase, the more `nil` check for errors there are, and it grows linearly with your code base, which is a great distraction from the main business logic.

I do understand (actually quite recently) that this is [a restriction](https://go.dev/doc/faq#exceptions) Go purposefully apply to the programmers, so that error handling will be explicitly addressed and traced in the code. It will be convenient when debugging (comparing to when writing the code) since the possible places the error emit from is explicitly found in the code instead of implicitly like when you're dealing with exceptions. But I still think the coding part could be clearer with some (maybe FP) magic.

#### Memory Management

Recently I came to understand that (automatic) memory management is one of the most important things to consider when designing a modern programming language, unless the language doesn't dynamically allocate language *at all* (which really is not possible). Typically there will be a mechanism that keeps track of the dynamically allocated memory (usually organized as objects) and determine if they are still going to be used or already useless and to be cleaned. This mechanism is usually done in [reference counting](https://en.wikipedia.org/wiki/Reference_counting), borrow checking (like in [rust](https://rustc-dev-guide.rust-lang.org/borrow_check.html)) or some other ways, and the useless objects will be removed either when we determine that alongside the run (which has less performance overhead), or taken care by and separate garbage collection thread/process.

I'm still not very familiar with how exactly every part works, but will find some time to look into it (since it's sort of interesting).

#### Some languages to learn

- Go, as I'm working full time with this language now
- Rust, since I'm a proud systems engineer now (I guess)
- Julia, maybe learn and implement some deep learning models with it
- Lua, to write a game in [PICO-8](https://www.lexaloffle.com/pico-8.php)
- Haskell, to learn (again) about functional programing

Also I would like to learn more about LLVM so that I can get a bit more serious when creating my next toy language.

In my opinion the hardest part for an intermediate programmer to learn a new programming language is to find something (project, problem, etc.) for him to actually use the new language at scope, otherwise it's very likely going to fail. Hope that doesn't happen to me.