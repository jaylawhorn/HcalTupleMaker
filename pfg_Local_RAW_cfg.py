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
                 0, #default value
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.int,
                 "Number of events to skip")

options.register('processEvents',
                 -1, #default value
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.int,
                 "Number of events to process")

options.register('inputFiles',
                 "file:B904_Integration_1000028339.root",
                 #"file:/eos/cms/store/group/dpg_hcal/comm_hcal/USC/run303898/USC_303898.root",
                 VarParsing.VarParsing.multiplicity.list,
                 VarParsing.VarParsing.varType.string,
                 "Input files")

options.register('outputFile',
                 "file:led_1000028339.root", #default value
                 #"file:test.root", #default value
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 "Output file")

options.parseArguments()

print "Skip events =", options.skipEvents
print "Process events =", options.processEvents
print "inputFiles =", options.inputFiles
print "outputFile =", options.outputFile


#------------------------------------------------------------------------------------
# Declare the process and input variables
#------------------------------------------------------------------------------------
process = cms.Process('PFG',eras.Run2_2017)##new

#------------------------------------------------------------------------------------
# Get and parse the command line arguments
#------------------------------------------------------------------------------------
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(options.processEvents) )
process.source = cms.Source("HcalTBSource",
    fileNames  = cms.untracked.vstring(options.inputFiles),
    skipEvents = cms.untracked.uint32(options.skipEvents),
)

process.TFileService = cms.Service("TFileService",
     fileName = cms.string(options.outputFile)
)

#------------------------------------------------------------------------------------
# import of standard configurations
#------------------------------------------------------------------------------------
#process.load('Configuration.Geometry.GeometryIdeal_cff'
process.load('Configuration.StandardSequences.Services_cff')##new
process.load('FWCore.MessageLogger.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = cms.untracked.int32(1000)
process.load('Configuration.EventContent.EventContent_cff')##new
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')##new
#process.load('Configuration.StandardSequences.RawToDigi_Data_cff')##new
process.load('Configuration.StandardSequences.Reconstruction_Data_cff')##new
process.load('Configuration.StandardSequences.EndOfProcess_cff')##new
process.load("EventFilter.HcalRawToDigi.HcalRawToDigi_cfi")
process.load("RecoLocalCalo.Configuration.hcalLocalReco_cff")##new
#process.hbhereco = process.hbheprereco.clone()
process.load("CondCore.CondDB.CondDB_cfi")##new
#process.load("CondCore.DBCommon.CondDBSetup_cfi")

#process.dump=cms.EDAnalyzer('EventContentAnalyzer')
process.dump = cms.EDAnalyzer("HcalDigiDump")

#------------------------------------------------------------------------------------
# Set up our analyzer
#------------------------------------------------------------------------------------
process.load("HCALPFG.HcalTupleMaker.HcalTupleMaker_cfi") # Dont want to use this, load modules individually
process.hcalTupleHFDigis.DoEnergyReco = False
process.hcalTupleHFDigis.FilterChannels = False
#process.load("HCALPFG.HcalTupleMaker.HcalTupleMaker_Tree_cfi")
#process.load("HCALPFG.HcalTupleMaker.HcalTupleMaker_Event_cfi")
#process.load("HCALPFG.HcalTupleMaker.HcalTupleMaker_HBHEDigis_cfi")
#process.hcalTupleHBHEDigis.DoEnergyReco = False
#process.load("HCALPFG.HcalTupleMaker.HcalTupleMaker_HODigis_cfi")
#process.hcalTupleHODigis.DoEnergyReco = False
#process.load("HCALPFG.HcalTupleMaker.HcalTupleMaker_HFDigis_cfi")
#process.hcalTupleHFDigis.DoEnergyReco = False
#process.load("HCALPFG.HcalTupleMaker.HcalTupleMaker_HcalUnpackerReport_cfi")
#process.load("HCALPFG.HcalTupleMaker.HcalTupleMaker_QIE10Digis_cfi")
#process.load("HCALPFG.HcalTupleMaker.HcalTupleMaker_QIE11Digis_cfi")
#process.hcalTupleHBHERecHits.source = cms.untracked.InputTag("hbheplan1")
#process.hcalTupleHBHEDigis.recHits = cms.untracked.InputTag("hbheplan1")




#------------------------------------------------------------------------------------
# Since this is a local run, make sure we're looking for the FEDs in the right place
#------------------------------------------------------------------------------------
process.hcalDigis.InputLabel = cms.InputTag("source")

#------------------------------------------------------------------------------------
# FED numbers
#------------------------------------------------------------------------------------
#process.hcalDigis.FEDs = cms.untracked.vint32(1115)
process.hcalDigis.FEDs = cms.untracked.vint32(1192,1194,1196)

#------------------------------------------------------------------------------------
# QIE10  Unpacker
#------------------------------------------------------------------------------------
process.qie10Digis = process.hcalDigis.clone()
process.qie10Digis.InputLabel = cms.InputTag("source") 
#process.qie10Digis.FEDs = cms.untracked.vint32(1132)

#------------------------------------------------------------------------------------
# QIE11  Unpacker
#------------------------------------------------------------------------------------
process.qie11Digis = process.hcalDigis.clone()##new
process.qie11Digis.InputLabel = cms.InputTag("source")##new
#process.qie11Digis.FEDs = cms.untracked.vint32(1114,1115)##new
process.qie11Digis.FEDs = cms.untracked.vint32(1192,1194,1196)##new

#------------------------------------------------------------------------------------
# Specify Global Tag
#------------------------------------------------------------------------------------
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
process.GlobalTag.globaltag = '90X_dataRun2_Prompt_v3'

#   EMAP Needed for H2 DATA
process.es_ascii = cms.ESSource('HcalTextCalibrations',
        input = cms.VPSet(
               cms.PSet(
                object = cms.string('ElectronicsMap'),
                #file = cms.FileInPath('HCALPFG/HcalTupleMaker/data/test_EMAP.txt')  # EMAP here!
                file = cms.FileInPath('HCALPFG/HcalTupleMaker/data/EMAP-kalinin_HTR0_rbx_61_62.txt')
               )
        )
)
process.es_prefer = cms.ESPrefer('HcalTextCalibrations', 'es_ascii')

# Output definition                                                                                                                          
#------------------------------------------------------------------------------------
# HcalTupleMaker sequence definition
#------------------------------------------------------------------------------------
process.tuple_step = cms.Sequence(
    #process.dump*
    # Make HCAL tuples: Event, run, ls number
    process.hcalTupleEvent*
    # Make HCAL tuples: FED info
    process.hcalTupleFEDs*
    # Make HCAL tuples: unpacker info
    process.hcalTupleUnpackReport*
    # Make HCAL tuples: digi info
    process.hcalTupleHBHEDigis*
    #process.hcalTupleHODigis*
    #process.hcalTupleHFDigis*
    #process.hcalTupleQIE10Digis*
    process.hcalTupleQIE11Digis*
    #process.hcalCosmicDigis*
    #    process.hcalTupleTriggerPrimitives*
    #    # Make HCAL tuples: digi info
    #process.hcalTupleHBHECosmicsDigis*
    #    process.hcalTupleHOCosmicsDigis*
    #    # Make HCAL tuples: digi info
    #    process.hcalTupleHBHEL1JetsDigis*
    #    process.hcalTupleHFL1JetsDigis*
    #    process.hcalTupleL1JetTriggerPrimitives*
    #    # Make HCAL tuples: reco info
    #process.hcalTupleHBHERecHits*
    #process.hcalTupleHFRecHits*
    #process.hcalTupleHcalNoiseFilters*
    #process.hcalTupleMuonTrack*
    #
    #process.hcalTupleHBHERecHitsMethod0*
    #process.hcalTupleHcalNoiseFiltersMethod0*
    #process.hcalTupleCaloJetMetMethod0*
    #    process.hcalTupleHORecHits*
    #    process.hcalTupleHFRecHits*
    #    # Trigger info
    #process.hcalTupleTrigger*
    
    #    process.hcalTupleTriggerObjects*
    #    # Make HCAL tuples: cosmic muon info
    # process.hcalTupleCosmicMuons*
    #    # Package everything into a tree
    #
    process.hcalTupleTree
)


#-----------------------------------------------------------------------------------
# Path and EndPath definitions
#-----------------------------------------------------------------------------------
process.preparation = cms.Path(
    # Unpack digis from RAW
    #process.tbunpack*
    process.hcalDigis*
    #process.qie10Digis*
    process.qie11Digis*
    # Do energy reconstruction
    #process.hbheprereco*
    #process.hbheplan1*
    #process.horeco*
    #process.hfreco*
    # Make the ntuples
    process.tuple_step
)
