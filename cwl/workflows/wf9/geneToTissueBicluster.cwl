#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool
baseCommand: [ GeneToTissueBicluster.py, get-data-frame, to-json, --orient, records ]
inputs:
  input_genes:
    type: string[]
    inputBinding:
      position: 0
      prefix: --input_genes
outputs:
  bicluster_list:
    type: stdout
stdout: geneToTissueBicluster.records.json