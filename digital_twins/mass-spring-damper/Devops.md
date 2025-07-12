# Mass Spring Damper

This example demonstrates the use DevOps features of the DTaaS platform.
The Gitlab DevOps pipelines are used for providing this feature in
the DTaaS.

The `.gitlab-ci.yml` file controls the sequence of executing the lifecycle
scripts of the example. The configuration format of `.gitlab-ci.yml`
permits specifying stages for execution of a program.
In this first example, all the lifecycle scripts are put in single stage,
namely *build_and_run*.

This example produces co-simulation outputs which are then saved in
the artifacts repository of the Gitlab. You can access them at
<https://gitlab.foo.com/dtaas/username/-/artifacts>.
