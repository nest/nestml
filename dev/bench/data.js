window.BENCHMARK_DATA = {
  "lastUpdate": 1771409097606,
  "repoUrl": "https://github.com/nest/nestml",
  "entries": {
    "Benchmark": [
      {
        "commit": {
          "author": {
            "name": "clinssen",
            "username": "clinssen"
          },
          "committer": {
            "name": "clinssen",
            "username": "clinssen"
          },
          "id": "e581058941ca0b842b6c56bf88b4a13e28aa0943",
          "message": "Fix confusion in logger between model name and artifact name",
          "timestamp": "2026-02-04T18:30:36Z",
          "url": "https://github.com/nest/nestml/pull/1308/commits/e581058941ca0b842b6c56bf88b4a13e28aa0943"
        },
        "date": 1771409097318,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/nest_continuous_benchmarking/test_nest_continuous_benchmarking.py::TestNESTContinuousBenchmarking::test_stdp_nn_synapse",
            "value": 0.3173060872404771,
            "unit": "iter/sec",
            "range": "stddev: 0.1603181723675924",
            "extra": "mean: 3.1515310932000147 sec\nrounds: 5"
          }
        ]
      }
    ]
  }
}