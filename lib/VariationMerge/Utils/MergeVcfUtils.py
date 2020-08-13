import subprocess
import os
import logging 


class MergeVcfUtils:
    def __init__(self):
        pass

    def bgzip_vcf(self, vcf_file):
        bgzip_cmd = ["bgzip"]
        bgzip_cmd.extend(["-c", vcf_file])
        outfile = vcf_file + ".gz"
        bgzip_cmd.extend([">", outfile])
        self.run_cmd(bgzip_cmd)
        return outfile

    def index_vcf(self, vcf_file):
        bgzipped_vcf = self.bgzip_vcf(vcf_file)
        index_cmd = ["tabix"]
        index_cmd.extend(["-p", "vcf" ])
        index_cmd.append(bgzipped_vcf)
        self.run_cmd(index_cmd)

    def run_cmd(self, cmd):
        """
        This function runs a third party command line tool
        eg. bgzip etc.
        :param command: command to be run
        :return: success
        """
        command = " ".join(cmd)
        print(command)
        logging.info("Running command " + command)
        cmdProcess = subprocess.Popen(command,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT,
                                      shell=True)
        for line in cmdProcess.stdout:
            logging.info(line.decode("utf-8").rstrip())
            cmdProcess.wait()
            logging.info('return code: ' + str(cmdProcess.returncode))
            if cmdProcess.returncode != 0:
                raise ValueError('Error in running command with return code: '
                                 + command
                                 + str(cmdProcess.returncode) + '\n')
        logging.info("command " + command + " ran successfully")
        return "success" 

    def merge_vcf(self, vcf_list, merge_output_file):
        command = ["bcftools"]
        command.extend(["merge", "--merge all"])
        command.extend(vcf_list)
        command.extend([">", merge_output_file])
        self.run_cmd(command)

if __name__ == "__main__":
   mv = MergeVcfUtils()
   mv.merge_vcf(["gatk_variation.fixed.vcf.gz", "jmc2_test.vcf.gz"], "merged_gatk_variation_jmc2_test.vcf")
