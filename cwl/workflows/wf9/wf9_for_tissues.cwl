#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: Workflow
inputs:
    input_genes:
        type: string
outputs:
  tissue_to_gene_bicluster_list:
    type: File
    outputSource: tissueToGeneBicluster/tissue_to_gene_bicluster_list
steps:
  tissueToGeneBicluster:
    run: tissueToGeneBicluster.cwl
    in:
      input_tissues: input_tissues
    out: [ tissue_to_gene_bicluster_list ]
