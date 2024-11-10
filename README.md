# eXperiment Shaperate

The eXperiment Shaperate (`xshaper`) is a tool and library for monitoring and
recording experimental runs.  It provides a few key capabilities:

- Measure time, resource consumption, power usage (when possible), and other
  statistics a computational job.
- Maintain a record of the history of computational jobs, even those used to
  generate past versions of a project or that failed outright, to maintain a
  record of resource usage over the course of a project.

This is partly inspired by [emers][], and our needs trying to record the
computational resources needed for experiments using the [LensKit][lk],
particularly the [LensKit Codex][codex].

[emers]: https://github.com/ISG-Siegen/emers
[lk]: https://lenskit.org
[codex]: https://codex.lenskit.org

> [!NOTE]
>
> The name comes from Dragon Age; like the Dwarven Shaperate keeps a record of
> dwarven families and activities, the eXperiment Shaperate records your
> experimental runs.
