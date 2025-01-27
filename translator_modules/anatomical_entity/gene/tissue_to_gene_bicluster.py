#!/usr/bin/env python3

# Workflow 9, Tissue-to-Gene Bicluster

import asyncio
import concurrent.futures
import urllib.request
from collections import defaultdict, Counter
from json import JSONDecodeError

import fire
import pandas as pd
import requests

from biolink.model import GeneToExpressionSiteAssociation, AnatomicalEntity, Gene

from translator_modules.core.module_payload import Payload
from translator_modules.core.data_transfer_model import ModuleMetaData, ConceptSpace

bicluster_tissue_url = 'https://bicluster.renci.org/RNAseqDB_bicluster_gene_to_tissue_v3_all_col_labels/'


class BiclusterByTissueToGene():
    def __init__(self):
        pass

    def get_ID_list(self, ID_list_url):
        with urllib.request.urlopen(ID_list_url) as url:
            ID_list = url.read().decode().split('\n')
        return ID_list

    def curated_ID_list(self, ID_list):
        curated_ID_list = []
        for ID in ID_list:
            if not ID:
                continue
            else:
                ID = ID.split(None, 1)[0]
                ID = ID.lower()
                curated_ID_list.append(ID)
        return curated_ID_list

    def run_getinput(self, ID_list_url):
        ID_list = self.get_ID_list(ID_list_url)
        curated_ID_list = self.curated_ID_list(ID_list)
        return curated_ID_list

    async def tissue_to_gene_biclusters_async(self, input_ID_list):
        bicluster_url_list = [bicluster_tissue_url + tissue + '/' + '?include_similar=true' for tissue in input_ID_list]
        length_bicluster_url_list = len(bicluster_url_list)
        all_biclusters_dict = defaultdict(dict)
        with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor_1:
            all_genes = []
            all_genes_dict = defaultdict(dict)
            loop_1 = asyncio.get_event_loop()
            futures_1 = [loop_1.run_in_executor(executor_1, requests.get, request_1_url) for request_1_url in
                         bicluster_url_list]
            for response in await asyncio.gather(*futures_1):

                try:
                    response_json = response.json()
                except JSONDecodeError:
                    continue

                for x in response_json:
                    gene = x['gene']
                    all_genes.append(gene)
            genes_counted = Counter(all_genes)
        return genes_counted.most_common()


class TissueToGeneBicluster(Payload):

    def __init__(self, input_tissues):

        super(TissueToGeneBicluster, self).__init__(
            module=BiclusterByTissueToGene(),
            metadata=ModuleMetaData(
                name="Mod9A - Tissue-to-Gene Bicluster",
                source='RNAseqDB Biclustering',
                association=GeneToExpressionSiteAssociation,
                domain=ConceptSpace(AnatomicalEntity, ['UBERON']),
                relationship='related_to',
                range=ConceptSpace(Gene, ['ENSEMBL'])
            )
        )

        input_tissue_ids = self.get_simple_input_identifier_list(input_tissues)

        most_common_tissues = asyncio.run(self.module.tissue_to_gene_biclusters_async(input_tissue_ids))

        self.results = pd.DataFrame.from_records(most_common_tissues, columns=["hit_id", "score"])


if __name__ == '__main__':
    fire.Fire(TissueToGeneBicluster)
