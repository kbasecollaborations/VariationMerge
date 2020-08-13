/*
A KBase module: VariationMerge
*/

module VariationMerge {
    typedef structure {
        string report_name;
        string report_ref;
    } ReportResults;

    /*
        This example function accepts any number of parameters and returns results in a KBaseReport
    */

    typedef structure{
        string obj_name;
        string workspace_name; 
        list <string> vcflist;   /*change it to featureset later*/
    } inparams;
   
    typedef structure {
        string output_obj_ref;
        string report_name;
        string report_ref;
    } ReportResults; 

    funcdef run_VariationMerge(inparams params) returns (ReportResults output) authentication required;

};
