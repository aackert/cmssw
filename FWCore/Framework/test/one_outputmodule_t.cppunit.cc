/*
 *  proxyfactoryproducer_t.cc
 *  EDMProto
 *
 *  Created by Chris Jones on 4/8/05.
 *  Changed by Viji Sundararajan on 28-Jun-05
 */
#include <iostream>
#include <atomic>
#include <vector>
#include <map>
#include <functional>
#include "FWCore/Framework/interface/one/OutputModule.h"
#include "FWCore/Framework/src/OutputModuleCommunicator.h"
#include "FWCore/Framework/src/WorkerT.h"
#include "FWCore/Framework/interface/OccurrenceTraits.h"
#include "DataFormats/Provenance/interface/ProductRegistry.h"
#include "DataFormats/Provenance/interface/BranchIDListHelper.h"
#include "FWCore/Framework/interface/HistoryAppender.h"
#include "FWCore/Utilities/interface/GlobalIdentifier.h"
#include "FWCore/Framework/interface/TriggerNamesService.h"
#include "FWCore/ServiceRegistry/interface/ParentContext.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "FWCore/ServiceRegistry/interface/ServiceRegistry.h"
#include "FWCore/Framework/interface/FileBlock.h"


#include "FWCore/Utilities/interface/Exception.h"

#include "cppunit/extensions/HelperMacros.h"

namespace edm {
  class ModuleCallingContext;
}

class testOneOutputModule: public CppUnit::TestFixture 
{
  CPPUNIT_TEST_SUITE(testOneOutputModule);
  
  CPPUNIT_TEST(basicTest);
  CPPUNIT_TEST(runTest);
  CPPUNIT_TEST(lumiTest);
  CPPUNIT_TEST(fileTest);
  CPPUNIT_TEST(resourceTest);
  
  CPPUNIT_TEST_SUITE_END();
public:
  testOneOutputModule();
  
  void setUp(){}
  void tearDown(){}

  void basicTest();
  void runTest();
  void lumiTest();
  void fileTest();
  void resourceTest();

private:

  enum class Trans {
    kBeginJob,
    kGlobalOpenInputFile,
    kGlobalBeginRun,
    kGlobalBeginRunProduce,
    kGlobalBeginLuminosityBlock,
    kEvent,
    kGlobalEndLuminosityBlock,
    kGlobalEndRun,
    kGlobalCloseInputFile,
    kEndJob
  };
  
  std::map<Trans,std::function<void(edm::Worker*)>> m_transToFunc;
  typedef std::vector<Trans> Expectations;
  
  edm::ProcessConfiguration m_procConfig;
  boost::shared_ptr<edm::ProductRegistry> m_prodReg;
  boost::shared_ptr<edm::BranchIDListHelper> m_idHelper;
  std::unique_ptr<edm::EventPrincipal> m_ep;
  edm::HistoryAppender historyAppender_;
  boost::shared_ptr<edm::LuminosityBlockPrincipal> m_lbp;
  boost::shared_ptr<edm::RunPrincipal> m_rp;
  edm::EventSetup* m_es = nullptr;
  edm::CurrentProcessingContext* m_context = nullptr;
  edm::ModuleDescription m_desc = {"Dummy","dummy"};
  edm::CPUTimer* m_timer = nullptr;
  edm::WorkerParams m_params;
  
  typedef edm::service::TriggerNamesService TNS;
  typedef edm::serviceregistry::ServiceWrapper<TNS> w_TNS;
  boost::shared_ptr<w_TNS> tnsptr_;
  edm::ServiceToken serviceToken_;
  
  template<typename T>
  void testTransitions(std::unique_ptr<T>&& iMod, Expectations const& iExpect);
  
  class BasicOutputModule : public edm::one::OutputModule<> {
  public:
    BasicOutputModule(edm::ParameterSet const& iPSet): edm::one::OutputModuleBase(iPSet),edm::one::OutputModule<>(iPSet){}
    unsigned int m_count = 0;
    
    void write(edm::EventPrincipal const&, edm::ModuleCallingContext const*) override {
      ++m_count;
    }
    void writeRun(edm::RunPrincipal const&, edm::ModuleCallingContext const*) override {
      ++m_count;
    }
    void writeLuminosityBlock(edm::LuminosityBlockPrincipal const&, edm::ModuleCallingContext const*) override {
      ++m_count;
    }

  };
  
  class RunOutputModule : public edm::one::OutputModule<edm::one::WatchRuns> {
  public:
    RunOutputModule(edm::ParameterSet const& iPSet) : edm::one::OutputModuleBase(iPSet), edm::one::OutputModule<edm::one::WatchRuns>(iPSet) {}
    unsigned int m_count = 0;
    void write(edm::EventPrincipal const&, edm::ModuleCallingContext const*) override {
      ++m_count;
    }
    void writeRun(edm::RunPrincipal const&, edm::ModuleCallingContext const*) override {
      ++m_count;
    }
    void writeLuminosityBlock(edm::LuminosityBlockPrincipal const&, edm::ModuleCallingContext const*) override {
      ++m_count;
    }
    
    void beginRun(edm::RunPrincipal const&, edm::ModuleCallingContext const*)  override {
      ++m_count;
    }

    void endRun(edm::RunPrincipal const&, edm::ModuleCallingContext const*)  override {
      ++m_count;
    }
  };


  class LumiOutputModule : public edm::one::OutputModule<edm::one::WatchLuminosityBlocks> {
  public:
    LumiOutputModule(edm::ParameterSet const& iPSet) : edm::one::OutputModuleBase(iPSet), edm::one::OutputModule<edm::one::WatchLuminosityBlocks>(iPSet) {}
    unsigned int m_count = 0;
    void write(edm::EventPrincipal const&, edm::ModuleCallingContext const*) override {
      ++m_count;
    }
    void writeRun(edm::RunPrincipal const&, edm::ModuleCallingContext const*) override {
      ++m_count;
    }
    void writeLuminosityBlock(edm::LuminosityBlockPrincipal const&, edm::ModuleCallingContext const*) override {
      ++m_count;
    }
    
    
    void beginLuminosityBlock(edm::LuminosityBlockPrincipal const&, edm::ModuleCallingContext const*)  override {
      ++m_count;
    }
    
    void endLuminosityBlock(edm::LuminosityBlockPrincipal const&, edm::ModuleCallingContext const*) override {
      ++m_count;
    }
  };
  class FileOutputModule : public edm::one::OutputModule<edm::WatchInputFiles> {
  public:
    FileOutputModule(edm::ParameterSet const& iPSet) : edm::one::OutputModuleBase(iPSet), edm::one::OutputModule<edm::WatchInputFiles>(iPSet) {}
    unsigned int m_count = 0;
    void write(edm::EventPrincipal const&, edm::ModuleCallingContext const*) override {
      ++m_count;
    }
    void writeRun(edm::RunPrincipal const&, edm::ModuleCallingContext const*) override {
      ++m_count;
    }
    void writeLuminosityBlock(edm::LuminosityBlockPrincipal const&, edm::ModuleCallingContext const*) override {
      ++m_count;
    }
    
    void respondToOpenInputFile(edm::FileBlock const&)  override {
      ++m_count;
    }
    
    void respondToCloseInputFile(edm::FileBlock const&) override {
      ++m_count;
    }
  };
  
  class ResourceOutputModule : public edm::one::OutputModule<edm::one::SharedResources> {
  public:
    ResourceOutputModule(edm::ParameterSet const& iPSet): edm::one::OutputModuleBase(iPSet),edm::one::OutputModule<edm::one::SharedResources>(iPSet){
      usesResource();
    }
    unsigned int m_count = 0;
    
    void write(edm::EventPrincipal const&, edm::ModuleCallingContext const*) override {
      ++m_count;
    }
    void writeRun(edm::RunPrincipal const&, edm::ModuleCallingContext const*) override {
      ++m_count;
    }
    void writeLuminosityBlock(edm::LuminosityBlockPrincipal const&, edm::ModuleCallingContext const*) override {
      ++m_count;
    }
    
  };


};

///registration of the test so that the runner can find it
CPPUNIT_TEST_SUITE_REGISTRATION(testOneOutputModule);

testOneOutputModule::testOneOutputModule():
m_prodReg(new edm::ProductRegistry{}),
m_idHelper(new edm::BranchIDListHelper{}),
m_ep()
{
  //Setup the principals
  m_prodReg->setFrozen();
  m_idHelper->updateRegistries(*m_prodReg);
  edm::EventID eventID;
  
  std::string uuid = edm::createGlobalIdentifier();
  edm::Timestamp now(1234567UL);
  boost::shared_ptr<edm::RunAuxiliary> runAux(new edm::RunAuxiliary(eventID.run(), now, now));
  m_rp.reset(new edm::RunPrincipal(runAux, m_prodReg, m_procConfig, &historyAppender_,0));
  boost::shared_ptr<edm::LuminosityBlockAuxiliary> lumiAux(new edm::LuminosityBlockAuxiliary(m_rp->run(), 1, now, now));
  m_lbp.reset(new edm::LuminosityBlockPrincipal(lumiAux, m_prodReg, m_procConfig, &historyAppender_,0));
  m_lbp->setRunPrincipal(m_rp);
  edm::EventAuxiliary eventAux(eventID, uuid, now, true);

  m_ep.reset(new edm::EventPrincipal(m_prodReg,
                                     m_idHelper,
                                     m_procConfig,nullptr));
  m_ep->fillEventPrincipal(eventAux);
  m_ep->setLuminosityBlockPrincipal(m_lbp);

  //For each transition, bind a lambda which will call the proper method of the Worker
  m_transToFunc[Trans::kGlobalOpenInputFile] = [this](edm::Worker* iBase) {
    edm::FileBlock fb;
    iBase->respondToOpenInputFile(fb);
  };


  m_transToFunc[Trans::kGlobalBeginRun] = [this](edm::Worker* iBase) {
    typedef edm::OccurrenceTraits<edm::RunPrincipal, edm::BranchActionGlobalBegin> Traits;
    edm::ParentContext parentContext;
    iBase->doWork<Traits>(*m_rp,*m_es,m_context,m_timer, edm::StreamID::invalidStreamID(), parentContext, nullptr); };
  
  m_transToFunc[Trans::kGlobalBeginLuminosityBlock] = [this](edm::Worker* iBase) {
    typedef edm::OccurrenceTraits<edm::LuminosityBlockPrincipal, edm::BranchActionGlobalBegin> Traits;
    edm::ParentContext parentContext;
    iBase->doWork<Traits>(*m_lbp,*m_es,m_context,m_timer, edm::StreamID::invalidStreamID(), parentContext, nullptr); };
  
  m_transToFunc[Trans::kEvent] = [this](edm::Worker* iBase) {
    typedef edm::OccurrenceTraits<edm::EventPrincipal, edm::BranchActionStreamBegin> Traits;
    edm::ParentContext parentContext;
    iBase->doWork<Traits>(*m_ep,*m_es,m_context,m_timer, edm::StreamID::invalidStreamID(), parentContext, nullptr); };

  m_transToFunc[Trans::kGlobalEndLuminosityBlock] = [this](edm::Worker* iBase) {
    typedef edm::OccurrenceTraits<edm::LuminosityBlockPrincipal, edm::BranchActionGlobalEnd> Traits;
    edm::ParentContext parentContext;
    iBase->doWork<Traits>(*m_lbp,*m_es,m_context,m_timer, edm::StreamID::invalidStreamID(), parentContext, nullptr);
    auto b =iBase->createOutputModuleCommunicator();
    CPPUNIT_ASSERT(b.get());
    b->writeLumi(*m_lbp, nullptr);
  };

  m_transToFunc[Trans::kGlobalEndRun] = [this](edm::Worker* iBase) {
    typedef edm::OccurrenceTraits<edm::RunPrincipal, edm::BranchActionGlobalEnd> Traits;
    edm::ParentContext parentContext;
    iBase->doWork<Traits>(*m_rp,*m_es,m_context,m_timer, edm::StreamID::invalidStreamID(), parentContext, nullptr);
    auto b = iBase->createOutputModuleCommunicator();
    CPPUNIT_ASSERT(b.get());
    b->writeRun(*m_rp, nullptr);
  };
  
  m_transToFunc[Trans::kGlobalCloseInputFile] = [this](edm::Worker* iBase) {
    edm::FileBlock fb;
    iBase->respondToCloseInputFile(fb);
  };


  // We want to create the TriggerNamesService because it is used in
  // the tests.  We do that here, but first we need to build a minimal
  // parameter set to pass to its constructor.  Then we build the
  // service and setup the service system.
  edm::ParameterSet proc_pset;
  
  std::string processName("HLT");
  proc_pset.addParameter<std::string>("@process_name", processName);
  
  std::vector<std::string> paths;
  edm::ParameterSet trigPaths;
  trigPaths.addParameter<std::vector<std::string>>("@trigger_paths", paths);
  proc_pset.addParameter<edm::ParameterSet>("@trigger_paths", trigPaths);
  
  std::vector<std::string> endPaths;
  proc_pset.addParameter<std::vector<std::string>>("@end_paths", endPaths);

  // Now create and setup the service
  tnsptr_.reset(new w_TNS(std::auto_ptr<TNS>(new TNS(proc_pset))));
  
  serviceToken_ = edm::ServiceRegistry::createContaining(tnsptr_);
  

}


namespace {
  template<typename T>
  void
  testTransition(T* iMod, edm::Worker* iWorker, testOneOutputModule::Trans iTrans, testOneOutputModule::Expectations const& iExpect, std::function<void(edm::Worker*)> iFunc) {
    assert(0==iMod->m_count);
    iFunc(iWorker);
    auto count = std::count(iExpect.begin(),iExpect.end(),iTrans);
    if(count != iMod->m_count) {
      std::cout<<"For trans " <<static_cast<std::underlying_type<testOneOutputModule::Trans>::type >(iTrans)<< " expected "<<count<<" and got "<<iMod->m_count<<std::endl;
    }
    CPPUNIT_ASSERT(iMod->m_count == count);
    iMod->m_count = 0;
    iWorker->reset();
  }
}

template<typename T>
void
testOneOutputModule::testTransitions(std::unique_ptr<T>&& iMod, Expectations const& iExpect) {
  T* pMod = iMod.get();
  edm::one::OutputWorker w{std::move(iMod),m_desc,m_params};
  for(auto& keyVal: m_transToFunc) {
    testTransition(pMod,&w,keyVal.first,iExpect,keyVal.second);
  }
}


void testOneOutputModule::basicTest()
{
  //make the services available
  edm::ServiceRegistry::Operate operate(serviceToken_);

  edm::ParameterSet pset;
  std::unique_ptr<BasicOutputModule> testProd{ new BasicOutputModule(pset) };
  
  CPPUNIT_ASSERT(0 == testProd->m_count);
  testTransitions(std::move(testProd), {Trans::kEvent,Trans::kGlobalEndLuminosityBlock, Trans::kGlobalEndRun});
}

void testOneOutputModule::runTest()
{
  //make the services available
  edm::ServiceRegistry::Operate operate(serviceToken_);

  edm::ParameterSet pset;
  std::unique_ptr<RunOutputModule> testProd{ new RunOutputModule(pset) };
  
  CPPUNIT_ASSERT(0 == testProd->m_count);
  testTransitions(std::move(testProd), {Trans::kGlobalBeginRun, Trans::kEvent, Trans::kGlobalEndLuminosityBlock, Trans::kGlobalEndRun, Trans::kGlobalEndRun});
}

void testOneOutputModule::lumiTest()
{
  //make the services available
  edm::ServiceRegistry::Operate operate(serviceToken_);

  edm::ParameterSet pset;
  std::unique_ptr<LumiOutputModule> testProd{ new LumiOutputModule(pset) };
  
  CPPUNIT_ASSERT(0 == testProd->m_count);
  testTransitions(std::move(testProd), {Trans::kGlobalBeginLuminosityBlock, Trans::kEvent, Trans::kGlobalEndLuminosityBlock, Trans::kGlobalEndLuminosityBlock, Trans::kGlobalEndRun});
}

void testOneOutputModule::fileTest()
{
  //make the services available
  edm::ServiceRegistry::Operate operate(serviceToken_);
  
  edm::ParameterSet pset;
  std::unique_ptr<FileOutputModule> testProd{ new FileOutputModule(pset) };
  
  CPPUNIT_ASSERT(0 == testProd->m_count);
  testTransitions(std::move(testProd), {Trans::kGlobalOpenInputFile, Trans::kEvent, Trans::kGlobalEndLuminosityBlock, Trans::kGlobalEndRun, Trans::kGlobalCloseInputFile});
}

void testOneOutputModule::resourceTest()
{
  //make the services available
  edm::ServiceRegistry::Operate operate(serviceToken_);
  
  edm::ParameterSet pset;
  std::unique_ptr<ResourceOutputModule> testProd{ new ResourceOutputModule(pset) };
  
  CPPUNIT_ASSERT(0 == testProd->m_count);
  testTransitions(std::move(testProd), {Trans::kEvent,Trans::kGlobalEndLuminosityBlock, Trans::kGlobalEndRun});
}

