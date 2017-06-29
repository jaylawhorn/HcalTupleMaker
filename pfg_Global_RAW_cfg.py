#------------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------------
import FWCore.ParameterSet.Config as cms
from Configuration.StandardSequences.Eras import eras
import FWCore.ParameterSet.VarParsing as VarParsing

#------------------------------------------------------------------------------------
# Options
#------------------------------------------------------------------------------------
options = VarParsing.VarParsing()

options.register('skipEvents',
                 0, # default value
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.int,
                 "Number of events to skip")

options.register('processEvents',
                 -1, # default value
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.int,
                 "Number of events to process")

options.register('inputFiles',
                 "/store/data/Run2017A/ZeroBias1/RAW/v1/000/294/736/00000/0CBDFB15-623E-E711-8931-02163E01A3AD.root",
                 VarParsing.VarParsing.multiplicity.list,
                 VarParsing.VarParsing.varType.string,
                 "Input files")

options.register('outputFile',
                 "HcalTupleMaker.root", # default value
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 "Output file")

options.parseArguments()

print " "
print "Using options:"
print " skipEvents    =", options.skipEvents
print " processEvents =", options.processEvents
print " inputFiles    =", options.inputFiles
print " outputFile    =", options.outputFile
print " "

#------------------------------------------------------------------------------------
# Declare the process and input variables
#------------------------------------------------------------------------------------
process = cms.Process('PFG',eras.Run2_2017)

#------------------------------------------------------------------------------------
# Get and parse the command line arguments
#------------------------------------------------------------------------------------
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(options.processEvents) )

process.source = cms.Source(
    "PoolSource",
    fileNames  = cms.untracked.vstring(options.inputFiles),
    skipEvents = cms.untracked.uint32(options.skipEvents)
    )

process.TFileService = cms.Service(
    "TFileService",
    fileName = cms.string(options.outputFile)
    )

#------------------------------------------------------------------------------------
# import of standard configurations
#------------------------------------------------------------------------------------
process.load('Configuration.StandardSequences.Services_cff')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = cms.untracked.int32(1000)
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.L1Reco_cff')
process.load('Configuration.StandardSequences.RawToDigi_Data_cff')
process.load('Configuration.StandardSequences.Reconstruction_Data_cff')
process.load("RecoLocalCalo.Configuration.hcalLocalReco_cff")

process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('RecoMET.METProducers.hcalnoiseinfoproducer_cfi')
process.load("CommonTools.RecoAlgos.HBHENoiseFilter_cfi")
process.load("CommonTools.RecoAlgos.HBHENoiseFilterResultProducer_cfi")
#process.load("CondCore.CondDB.CondDB_cfi")
process.load("CondCore.DBCommon.CondDBSetup_cfi")

process.dump=cms.EDAnalyzer('EventContentAnalyzer')

process.es_pool = cms.ESSource("PoolDBESSource",
                               process.CondDBSetup,
                               timetype = cms.string('runnumber'),
                               toGet = cms.VPSet(
        cms.PSet(record = cms.string("HcalRecoParamsRcd"),
                 tag = cms.string("HcalRecoParams_HEP17shape205")
                 )
        ),
                               connect = cms.string('frontier://FrontierProd/CMS_CONDITIONS'),
                               authenticationMethod = cms.untracked.uint32(0)
                               )
process.es_prefer_es_pool = cms.ESPrefer( "PoolDBESSource", "es_pool" )

#------------------------------------------------------------------------------------
# Set up our analyzer
#------------------------------------------------------------------------------------
process.load("HCALPFG.HcalTupleMaker.HcalTupleMaker_cfi") # loads all modules
## set desired parameters, for example:
process.hcalTupleHFDigis.DoEnergyReco = True
process.hcalTupleHFDigis.FilterChannels = False
process.hcalTupleHFDigis.ChannelFilterList = cms.untracked.VPSet(
    # Notice only channels listed here will be saved, if the FilterChannels flag is set to true
    cms.PSet(iEta = cms.int32(29), iPhi = cms.int32(39), depth = cms.int32(1)),
    )
#process.hcaTupleRecHits.source = cms.string("hbheprereco")

from Configuration.StandardSequences.RawToDigi_Data_cff import *
process.CustomizedRawToDigi = cms.Sequence(
        gtDigis*
        #siPixelDigis*
        #siStripDigis*
        #ecalDigis*
        #ecalPreshowerDigis*
        hcalDigis
        #muonDTDigis*
        #muonCSCDigis*
        #muonRPCDigis*
        #castorDigis*
        #scalersRawToDigi*
        #tcdsDigis
)

#------------------------------------------------------------------------------------
# FED numbers 
#------------------------------------------------------------------------------------
#process.hcalDigis.FEDs = cms.untracked.vint32(	1100, 1102, 1104, # HBHEa 
#                                              	1106, 1108, 1110, # HBHEb
#                                              	1112, 1114, 1116, # HBHEc
#                                              	1118, 1120, 1122, # HF
#                                              	1119, 1121, 1123  # HF
#					        724, 725, 726, 727, 728, 729, 730, 731, # HO
# 					        1134 # HcalLaser
#                                              )

#------------------------------------------------------------------------------------
# QIE10  Unpacker
#------------------------------------------------------------------------------------
process.qie10Digis = process.hcalDigis.clone()
#process.qie10Digis.FEDs = cms.untracked.vint32(1118,1120,1122,1119,1121,1123)

#------------------------------------------------------------------------------------
# QIE11  Unpacker
#------------------------------------------------------------------------------------
process.qie11Digis = process.hcalDigis.clone()
process.qie11Digis.InputLabel = cms.InputTag("rawDataCollector")
process.qie11Digis.FEDs = cms.untracked.vint32(1114,1115)

#------------------------------------------------------------------------------------
# Specify Global Tag
#------------------------------------------------------------------------------------
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
process.GlobalTag.globaltag = '90X_dataRun2_Prompt_v3'
print "GlobalTag = ", str(process.GlobalTag.globaltag).split("'")[1]
print " "

#------------------------------------------------------------------------------------
# Create Noise Filter
#------------------------------------------------------------------------------------
# Could be out of date, commented out in the main sequence, need to be fixed
process.hcalnoise.fillCaloTowers = cms.bool(False)
process.hcalnoise.fillTracks = cms.bool(False)
process.ApplyBaselineHBHENoiseFilter = cms.EDFilter(
    'BooleanFlagFilter',
    inputLabel = cms.InputTag('HBHENoiseFilterResultProducer','HBHENoiseFilterResult'),
    reverseDecision = cms.bool(False)
    )


#process.hbheprereco.ts4chi2 = cms.double(99999.);
#process.hbheprereco.timeMin = cms.double(-100);
#process.hbheprereco.timeMax = cms.double( 100);
#process.hbheprereco.applyTimeConstraint = cms.bool(False);

#------------------------------------------------------------------------------------
# HcalTupleMaker sequence definition
#------------------------------------------------------------------------------------
process.tuple_step = cms.Sequence(
    #process.dump*
    ## Make HCAL tuples: Event info
    process.hcalTupleEvent*
    
    ## Make HCAL tuples: FED info
    #process.hcalTupleFEDs*
    
    ## Make HCAL tuples: digi info
    process.hcalTupleHBHEDigis*
    #process.hcalTupleHODigis*
    #process.hcalTupleHFDigis*
    #process.hcalTupleQIE10Digis* # for HF
    process.hcalTupleQIE11Digis* # for HEP17
    
    ## Make HCAL tuples: reco info
    process.hcalTupleHBHERecHits*
    #process.hcalTupleHFRecHits*
    #process.hcalTupleHORecHits*
    #process.hcalTupleHFRecHits*

    ## Make HCAL tuples: trigger info
    #process.hcalTupleTrigger*
    #process.hcalTupleTriggerPrimitives*
    #process.hcalTupleTriggerObjects*

    ## Package everything into a tree
    process.hcalTupleTree
)

#-----------------------------------------------------------------------------------
# Path and EndPath definitions
#-----------------------------------------------------------------------------------
process.preparation = cms.Path(
    ## Unpack digis from RAW
    #process.RawToDigi*
    #process.CustomizedRawToDigi*
    process.hcalDigis*
    #process.qie10Digis*
    process.qie11Digis*
    
    ## reconstruction 
    process.L1Reco*
    #process.reconstruction*
    #process.hcalLocalRecoSequence*
    
    ## Do energy reconstruction
    process.hbheprereco*
    #process.hbhereco*
    #process.horeco*
    #process.hfreco*
    
    ## For noise filter
    #process.hcalnoise*
    #process.HBHENoiseFilterResultProducer*
    #process.ApplyBaselineHBHENoiseFilter*
    
    ## Make the ntuples
    process.tuple_step
)
