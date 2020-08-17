# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
from installed_clients.WorkspaceClient import Workspace
from installed_clients.VariationUtilClient import VariationUtil 
from installed_clients.KBaseReportClient import KBaseReport
from VariationMerge.Utils.MergeVcfUtils import MergeVcfUtils
#END_HEADER


class VariationMerge:
    '''
    Module Name:
    VariationMerge

    Module Description:
    A KBase module: VariationMerge
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = "https://github.com/kbasecollaborations/VariationMerge.git"
    GIT_COMMIT_HASH = "918495236305bcae5e2ded0be6ed18d71defd678"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.shared_folder = config['scratch']
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        self.ws_url = config['workspace-url']

        self.vu = VariationUtil(self.callback_url)
        self.mu = MergeVcfUtils()
        #END_CONSTRUCTOR
        pass


    def run_VariationMerge(self, ctx, params):
        """
        :param params: instance of type "inparams" (This example function
           accepts any number of parameters and returns results in a
           KBaseReport) -> structure: parameter "obj_name" of String,
           parameter "workspace_name" of String, parameter "vcflist" of list
           of String
        :returns: instance of type "OutResults" -> structure: parameter
           "output_obj_ref" of String, parameter "report_name" of String,
           parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_VariationMerge

        self.ws = Workspace(url=self.ws_url, token=ctx['token'])

        print(params)

        vcf_flist = []
        assembly_ref_set = set()
        sampleset_ref_set = set()
        genome_set_ref_set = set()
        for i in range(len(params['vcflist'])):
            variation_ref = params['vcflist'][i]

            variation_obj = self.ws.get_objects2({'objects': [{'ref': variation_ref}]})['data'][0]
            print(variation_obj['data']['assembly_ref'])

            if 'assembly_ref' in variation_obj['data']:
                assembly_ref = variation_obj['data']['assembly_ref']
                assembly_ref_set.add(assembly_ref)
            elif 'genome_ref' in variation_obj['data']:
                genome_ref = variation_obj['data']['genome_ref']
                genome_set_ref_set.add(genome_ref)


            print(params['vcflist'][i])
            vcf_filename = "/kb/module/work/tmp/variation" + str(i) + ".vcf.gz"
            vcf_flist.append(vcf_filename)

            inparams = {}
            inparams['variation_ref'] = variation_ref
            inparams['filename'] = vcf_filename

            self.vu.get_variation_as_vcf(inparams)
            os.rename("/kb/module/work/tmp/variation.vcf.gz", vcf_filename)
            self.mu.index_vcf(vcf_filename)
            var_object_ref = params['vcflist'][i] 
            data = self.ws.get_objects2( {'objects':[{"ref":var_object_ref, 'included': ['/sample_set_ref']}]})['data'][0]['data']
            sampleset_ref_set.add(data['sample_set_ref'])

        #Raising exception

        if(len(genome_set_ref_set) == 0 and len(assembly_ref_set) != 1):
            raise Exception("variation objects are from different assembly refs")
        elif(len(sampleset_ref_set) != 1):
            raise Exception("variation objects are from different sample set refs")
        elif(len(assembly_ref_set) == 0 and len(genome_set_ref_set) != 1):
            raise Exception("variation objects are from different genome set refs")

        merged_file = os.path.join(self.shared_folder, "merged_gatk_variation_jmc2_test.vcf")
        self.mu.merge_vcf(vcf_flist, merged_file)

        save_variation_params = { 'workspace_name': params['workspace_name'],
            'genome_or_assembly_ref': assembly_ref_set.pop(),
            'sample_set_ref': sampleset_ref_set.pop(),
            'sample_attribute_name':'sample_attr',
            'vcf_staging_file_path': merged_file,
            'variation_object_name': params['variation_object_name']
        } 
        self.vu.save_variation_from_vcf(save_variation_params)


        report = KBaseReport(self.callback_url)
        report_info = report.create({'report': {'objects_created':[],
                                                'text_message': 'success'},
                                                'workspace_name': params['workspace_name']})
        output = {
            'report_name': report_info['name'],
            'report_ref': report_info['ref'],
        }
        #END run_VariationMerge

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_VariationMerge return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
