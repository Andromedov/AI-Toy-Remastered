---
name: Bug report
about: Let us know about a crash or bug.
title: "[BUG] "
labels: ''
assignees: Andromedov
body:
  - type: textarea
    id: description
    attributes:
      label: Describe the issue
      description: |
        A clear and concise description of what the problem is. 
        What did you expect to happen? What happened instead? How can we reproduce the problem?
    validations:
      required: true
  - type: input
    id: logs
    attributes:
      label: Relevant log output
      description: If applicable, upload your logs to a paste website like https://www.toptal.com/developers/hastebin, and paste the link here.
      placeholder: ex. https://hastebin.com/share/ihejenagob.rust
    validations:
      required: false
  - type: textarea
    id: extra
    attributes:
      label: Extra information
      description: |
        Feel free to add any additional info here. e.g. screenshots/videos, config files.
    validations:
      required: false
---
