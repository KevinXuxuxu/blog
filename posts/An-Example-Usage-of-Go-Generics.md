---
title: An Example Usage of Go Generics
date: 2023-02-27 06:18:14
tags: ["Go", "Programing Language", "Generics"]
category: tech
---

I haven't talked a lot about my new job at Google since last April, but I'm working in the performance engineering team who designs, implements and monitors performance benchmarks for a relatively new database product. Last year I took on a piece of work to start refactoring our benchmark framework to reduce the complexity of the codebase and make it easier to add or modify benchmarks. I'm sort of excited about this work as it would be my first time working on a large scope production level Go codebase. Alongside other refactoring work I did, one particular work of reducing boilerplate code utilizes [Go generics](https://go.dev/doc/tutorial/generics), which is a new feature of the Go language, that I find interesting enough to write about now.

##### The Problem

Assume you want to parse a bunch of different set of configs into Go [protocol buffer](https://github.com/protocolbuffers/protobuf) objects from [prototext](https://pkg.go.dev/google.golang.org/protobuf/encoding/prototext) files through [Unmarshal function](https://pkg.go.dev/google.golang.org/protobuf/encoding/prototext#Unmarshal). These configs are for different kind of benchmarks but share some common attributes from the top. For each proto definition of a specific kind of benchmark, there's a corresponding aggregated proto definition which is just a repeatable of the single proto, which allows loading config and running benchmarks in batch. For example:

```proto
// config definition for benchmark A
message AConfig {
    optional TestConfig test_config = 1;
    map<string, string> env_vars = 2;
    map<string, string> db_vars = 3;
}

message AConfigs {
    repeated AConfig config = 1;
}

// config definition for benchmark B
message BConfig {
    optional TestConfig test_config = 1;
    map<string, string> other_vars = 2;
}

message BConfigs {
    repeated BConfig config = 1;
}
```

Note that for `A/BConfig`, the only guarantee is that they will have a `test_config`, which contains the common config for all benchmarks; and `A/BConfigs` is just repeated of them correspondingly.

Getting back to **the problem**: you want to write a single set of logic that could parse all kinds of prototext into a data structure (let's call it `ConfigDB`) where you can search for a specific config based on a subset of configs contained in `TestConfig`.

##### The Fake Solution

In the beginning I wan't thinking of using generics, since I always have an intuition that "generics only works for the case when you don't have any constraint on the behavior of the subject", like all the STL data structures in Java.

As a result, I tried to use interface which can apply constraints to the behavior of the types we want to model. Ideally, you would want to make an interface that models `A/BConfigs` so that it can be created using `Unmarshal`. It would be something like this:

```Go
type configPb interface {
    GetTestConfig() *pb.TestConfig
}

type configsPb interface {
    proto.Message
    GetConfig() []configPb
}
```

But the problem is obvious, `Unmarshal` takes in a `proto.Message` object, which you cannot create without a concrete type. You're able to create an [interface value](https://go.dev/tour/methods/11) by doing a cast, but it will still fail because the concrete type doesn't actually implement the correct function:

```Go
// if you do the following
var cfgs pb.AConfigs
cfgsInterface := configsPb(cfgs)

// you will get compiler error
./prog.go:52:12: cannot convert cfgs (variable of type pb.AConfigs) to type configsPb: pb.AConfigs does not implement configsPb (wrong type for method GetConfig)
		have GetConfig() []*pb.AConfig
		want GetConfig() []configPb
```

I tend to believe that interface in Go alone is not able to model this kind of "nested behaviors". So we will have to use generics together with interface as constraints, which is mentioned in the later part of [go official introduction to generics](https://go.dev/doc/tutorial/generics).

##### The Solution
Without further ado, here is the solution I got:

```Go
type Key struct {...}

func NewKey(testConfig *pb.TestConfig) Key {...}

interface configPb {
    GetTestConfig() *pb.TestConfig
}

type ConfigDB struct {
    configs map[Key]configPb
}

func New[D configPb, T any, M interface{
    proto.Message
    GetConfig() []D
    *T
}](configs [][]byte) (*ConfigDB, error) {
    c := &ConfigDB{
        configs: make(map[Key]configPb)
    }
    for _, configBytes := range configs {
        cfgs := M(new(T))
        if err := prototext.Unmarshal(configBytes, cfgs); err != nil {
            return err
        }
        for _, cfg := range cfgs.GetConfig() {
            key := NewKey(cfg.GetTestConfig())
            c.configs[key] = cfg
        }
    }
    return c
}
```

Several things to notice:
- `ConfigDB` uses a map to achieve the search config feature, and the `Key` type is constructed from information from `pb.TestConfig` which all configs should have.
- Using an interface `configPb` to model all single config types, which is similar to what we have in the previous section. But modeling for aggregated config types are done by generics:

```Go
func New[D configPb, T any, M interface{
    proto.Message       // need to be a proto.Message to be Unmarshalled
    GetConfig() []D     // models the GetConfig method with correct type D (which will be e.g. AConfig)
    *T                  // the above constraints will be applied to T
}]...
```

- And when you parse and actually use the configs:

```Go
// configs is a [][]byte we got from some magic internal build rule

configDb, err := configdb.New[*pb.AConfig, pb.AConfigs](configs)

// key is a Key constructed through other benchmark selection logic

config, ok := configDb.configs[key].(*pb.AConfig)  // config would be *pb.AConfig
```

Note that you could also get rid of the type cast from `configPb` to `*pb.AConfig` by making `configDB` a generic type, but we're just making a trade off between type safety and verbosity. In production `configDB` is much more complicated and very frequently used, so less verbosity is more important.

Before this refactor, every kind of benchmark repeats the same `configDB` logic with their own config types, while over 500 boilerplate code was removed after this refactor. With the advanced compiler information of Go language, I would highly recommend anyone facing same problems to try go generics.
