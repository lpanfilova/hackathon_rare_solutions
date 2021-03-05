import pandas as pd
import xml.etree.ElementTree as ET

from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)

# Converting phenotypes.xml to pandas dataframe

data_for_df = []

root = ET.parse('phenotypes.xml').getroot()
hpo_disorder_set_status_list = root.findall('HPODisorderSetStatusList')[0]
hpo_disorder_set_statuses = hpo_disorder_set_status_list.findall('HPODisorderSetStatus')

for node in hpo_disorder_set_statuses:
    # Exactly 1 disorder per HPODisorderSetStatus
    disorder = node.findall('Disorder')[0]
    disorder_name = disorder.findall('Name')[0].text
    disorder_type = disorder.findall('DisorderType')[0].findall('Name')[0].text
    disorder_group = disorder.findall('DisorderGroup')[0].findall('Name')[0].text
    

    
    hpo_disorder_association_list = disorder.findall('HPODisorderAssociationList')[0]
    hpo_disorder_associations = hpo_disorder_association_list.findall('HPODisorderAssociation')
    
    for association in hpo_disorder_associations:
        hpo_term = association.findall('HPO')[0].findall('HPOTerm')[0].text
        hpo_freq = association.findall('HPOFrequency')[0].findall('Name')[0].text 
        
        data_for_df.append({'DisorderName' : disorder_name,
                            'DisorderType' : disorder_type,
                            'DisorderGroup' : disorder_group,
                            'AssociatedHPO' : hpo_term,
                            'HPOFrequency' : hpo_freq})
        
hpo_df = pd.DataFrame(data_for_df)  

# Converting genes.xml to pandas dataframe

data_for_df = []

root = ET.parse('genes.xml').getroot()
disorder_list = root.findall('DisorderList')[0]
disorders = disorder_list.findall('Disorder') 


for disorder in disorders:
    disorder_name = disorder.findall('Name')[0].text
    disorder_type = disorder.findall('DisorderType')[0].findall('Name')[0].text
    disorder_group = disorder.findall('DisorderGroup')[0].findall('Name')[0].text


    disorder_gene_association_list = disorder.findall('DisorderGeneAssociationList')[0]
    disorder_gene_associations = disorder_gene_association_list.findall('DisorderGeneAssociation')
    
    for association in disorder_gene_associations:
        gene = association.findall('Gene')[0].findall('Name')[0].text
        gene_symbol = association.findall('Gene')[0].findall('Symbol')[0].text
        gene_type = association.findall('Gene')[0].findall('GeneType')[0].findall('Name')[0].text
        disorder_gene_association_type = association.findall('DisorderGeneAssociationType')[0].findall('Name')[0].text

        data_for_df.append({'DisorderName' : disorder_name,
                            'DisorderType' : disorder_type,
                            'DisorderGroup' : disorder_group,
                            'AccociatedGene' : gene,
                            'GeneSymbol' : gene_symbol,
                            'GeneType': gene_type,
                            'GeneTypeAssociation': disorder_gene_association_type})
        
gene_df = pd.DataFrame(data_for_df)  

# Converting epidemiology.xml to pandas dataframe

data_for_df = []

root = ET.parse('epidemiology.xml').getroot()
disorder_list = root.findall('DisorderList')[0]
disorders = disorder_list.findall('Disorder') 

for disorder in disorders:
    disorder_name = disorder.findall('Name')[0].text
    disorder_type = disorder.findall('DisorderType')[0].findall('Name')[0].text
    disorder_group = disorder.findall('DisorderGroup')[0].findall('Name')[0].text


    disorder_prevalence_list = disorder.findall('PrevalenceList')[0]
    disorder_prevalences = disorder_prevalence_list.findall('Prevalence')
    
    for prevalence in disorder_prevalences:
        prevalence_type = prevalence.findall('PrevalenceType')[0].findall('Name')[0].text
        prevalence_qualification = prevalence.findall('PrevalenceQualification')[0].findall('Name')[0].text
        prevalence_geographic = prevalence.findall('PrevalenceGeographic')[0].findall('Name')[0].text
        prevalence_validation = prevalence.findall('PrevalenceValidationStatus')[0].findall('Name')[0].text

        data_for_df.append({'DisorderName' : disorder_name,
                            'DisorderType' : disorder_type,
                            'DisorderGroup' : disorder_group,
                            'PrevalenceType' : prevalence_type,
                            'PrevalenceQualification' : prevalence_qualification,
                            'PrevalenceGeographic': prevalence_geographic,
                            'PrevalenceValidationStatus': prevalence_validation})
        
df_epidem = pd.DataFrame(data_for_df) 





@app.route('/search')
@cross_origin()
def hello_world():
    #pheno = request.args.get('pheno')
    user_input = request.args.get('p')
    print(user_input)
    user_input = user_input.split(',')
    print(user_input)
    user_input = [e.strip() for e in user_input]
    print(user_input)
    
    #user_input = ['Macrocephaly', 'Intellectual disability', 'Seizures']
    matched_hpo_df_rows = hpo_df[hpo_df.AssociatedHPO.isin(user_input)]
    unique_disorders = matched_hpo_df_rows.DisorderName.unique()

    response = {}
    disorder_objects = []

    for disorder in unique_disorders:
        disorder_obj = {}
        
        matched_disorder_hpo_df_rows = matched_hpo_df_rows[matched_hpo_df_rows.DisorderName == disorder]
        matched_disorder_gene_df_rows = gene_df[gene_df.DisorderName == disorder]
        matched_disorder_df_epidem_rows = df_epidem[df_epidem.DisorderName == disorder]
        disorder_phenotypes = list(matched_disorder_hpo_df_rows.AssociatedHPO)
        
        if not set(user_input).issubset(set(disorder_phenotypes)):
            continue
        
        disorder_obj['name'] = disorder
        disorder_obj['phenotypes'] = disorder_phenotypes
        disorder_obj['frequencies'] = list(matched_disorder_hpo_df_rows.HPOFrequency)
        disorder_obj['genes'] = list(matched_disorder_gene_df_rows.AccociatedGene)
        disorder_obj['geography'] = list(matched_disorder_df_epidem_rows.PrevalenceGeographic.unique())
        disorder_objects.append(disorder_obj)
        
    response['disorders'] = disorder_objects
        
    return response