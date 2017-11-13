
/***************************************************Project Mutator****************************************************/
//-*-c++-*-
/*first line intentionally left blank.*/
/*Copyright (C) 2017 Farzad Sadeghi

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.*/
/*code structure inspired by Eli Bendersky's tutorial on Rewriters.*/
/**********************************************************************************************************************/
/*FIXME-all classes should use replacements.*/
/**********************************************************************************************************************/
/*included modules*/
/*project headers*/
#include "../mutator_aux.h"
/*standard headers*/
#include <string>
#include <iostream>
#include <cassert>
#include <vector>
/*LLVM headers*/
#include "clang/AST/AST.h"
#include "clang/AST/ASTConsumer.h"
#include "clang/ASTMatchers/ASTMatchers.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"
#include "clang/Basic/LLVM.h"
#include "clang/CodeGen/CodeGenAction.h"
#include "clang/CodeGen/BackendUtil.h"
#include "clang/Frontend/CompilerInstance.h"
#include "clang/Frontend/FrontendActions.h"
#include "clang/Lex/Lexer.h"
#include "clang/Tooling/CommonOptionsParser.h"
#include "clang/Tooling/Tooling.h"
#include "clang/Rewrite/Core/Rewriter.h"
#include "llvm/ADT/ArrayRef.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/LLVMContext.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/BasicBlock.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/Function.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Linker/Linker.h"
/**********************************************************************************************************************/
/*used namespaces*/
using namespace llvm;
using namespace clang;
using namespace clang::ast_matchers;
using namespace clang::driver;
using namespace clang::tooling;
/**********************************************************************************************************************/
/*global vars*/

static llvm::cl::OptionCategory MatcherSampleCategory("Matcher Sample");
/**********************************************************************************************************************/
//#define DBG
/**********************************************************************************************************************/
// kill all comments
/**********************************************************************************************************************/
// kill all whitespace, add , and ;
/**********************************************************************************************************************/
class CalledFunc : public MatchFinder::MatchCallback {
  public:
    CalledFunc(Rewriter &Rewrite) : Rewrite(Rewrite) {}

    virtual void run(const MatchFinder::MatchResult &MR) {
      if (MR.Nodes.getNodeAs<clang::CallExpr>("calledfunc") != nullptr) {
        const CallExpr *CE = MR.Nodes.getNodeAs<clang::CallExpr>("calledfunc");
        std::string name = CE->getDirectCallee()->getNameInfo().getAsString();
        std::size_t hash = std::hash<std::string>{}(name);
        std::string newname = "ID" + std::to_string(hash);
#ifdef DBG
        std::cout << "CallExpr name: "  << name << " Hash: " << hash << " New ID: " << newname << "\n";
#endif

        auto dummy = Rewrite.getRewrittenText(SourceRange(CE->getLocStart(), CE->getRParenLoc()));
        auto LParenOffset = dummy.find("(");
        dummy = Rewrite.getRewrittenText(SourceRange(CE->getLocStart(), CE->getLocStart().getLocWithOffset(LParenOffset - 1U)));
        Rewrite.ReplaceText(SourceRange(CE->getLocStart(), CE->getLocStart().getLocWithOffset(LParenOffset - 1U)), StringRef(newname));
      }
    }

  private:
    Rewriter &Rewrite;
};
/**********************************************************************************************************************/
class CalledVar : public MatchFinder::MatchCallback {
  public:
    CalledVar (Rewriter &Rewrite) : Rewrite(Rewrite) {}

    virtual void run(const MatchFinder::MatchResult &MR) {
      if (MR.Nodes.getNodeAs<clang::DeclRefExpr>("calledvar") != nullptr) {
        const DeclRefExpr* DRE = MR.Nodes.getNodeAs<clang::DeclRefExpr>("calledvar");
        auto name = DRE->getNameInfo().getAsString();
        std::size_t hash = std::hash<std::string>{}(name);
        std::string newname = "ID" + std::to_string(hash);
#ifdef DBG
        std::cout << "DeclRefExpr name: "  << name << " Hash: " << hash << " New ID: " << newname << "\n";
#endif
      SourceLocation SL = DRE->getNameInfo().getBeginLoc();
      SourceLocation SLE = DRE->getNameInfo().getEndLoc();

      Rewrite.ReplaceText(SourceRange(SL, SLE), StringRef(newname));
      }
    }

  private:
    Rewriter &Rewrite;
};
/**********************************************************************************************************************/
class FuncDecl : public MatchFinder::MatchCallback
{
public:
  FuncDecl (Rewriter &Rewrite) : Rewrite (Rewrite) {}

  virtual void run(const MatchFinder::MatchResult &MR)
  {
    if (MR.Nodes.getNodeAs<clang::FunctionDecl>("funcdecl") != nullptr) {
      const FunctionDecl* FD = MR.Nodes.getNodeAs<clang::FunctionDecl>("funcdecl");
      std::string funcname = FD->getNameInfo().getAsString();
      if (funcname == "main") return void();
      std::size_t hash = std::hash<std::string>{}(funcname);
      std::string newname = "ID" + std::to_string(hash);
#ifdef DBG
      std::cout << "Function name: "  << funcname << " Hash: " << hash << " New ID: " << newname << "\n";
#endif

      SourceLocation SL = FD->getNameInfo().getBeginLoc();
      SourceLocation SLE = FD->getNameInfo().getEndLoc();

      Rewrite.ReplaceText(SourceRange(SL, SLE), StringRef(newname));
    }
  }

private:
  Rewriter &Rewrite;
};
/**********************************************************************************************************************/
class VDecl : public MatchFinder::MatchCallback
{
public:
  VDecl (Rewriter &Rewrite) : Rewrite (Rewrite) {}

  virtual void run(const MatchFinder::MatchResult &MR)
  {
    if (MR.Nodes.getNodeAs<clang::VarDecl>("vardecl") != nullptr) {
      const VarDecl* VD = MR.Nodes.getNodeAs<clang::VarDecl>("vardecl");
      std::string varname = VD->getIdentifier()->getName().str();
      std::size_t hash = std::hash<std::string>{}(varname);
      std::string newname = "ID" + std::to_string(hash);
#ifdef DBG
      std::cout << "Var name: "  << varname << " Hash: " << hash << " New ID: " << newname << "\n";
#endif

      SourceLocation SL = VD->getLocation();
      SourceLocation SLE = VD->getLocEnd();

      Rewrite.ReplaceText(SourceRange(SL, SLE), StringRef(newname));
    }
  }

private:
  Rewriter &Rewrite;
};
/**********************************************************************************************************************/
class ClassDecl : public MatchFinder::MatchCallback {
  public:
    ClassDecl (Rewriter &Rewrite) : Rewrite(Rewrite) {}

    virtual void run(const MatchFinder::MatchResult &MR) {
      if (MR.Nodes.getNodeAs<clang::RecordDecl>("classdecl") != nullptr) {
        const RecordDecl* RD = MR.Nodes.getNodeAs<clang::RecordDecl>("classdecl");
        if (RD->isAnonymousStructOrUnion()) return void();
        if (RD->isInjectedClassName()) {}
        else {return void();}
        auto TD = RD->getCanonicalDecl();
        std::string varname = RD->getIdentifier()->getName().str();
        std::size_t hash = std::hash<std::string>{}(varname);
        std::string newname = "ID" + std::to_string(hash);
#ifdef DBG
        std::cout << "Record name: "  << varname << " Hash: " << hash << " New ID: " << newname << "\n";
#endif

        SourceLocation SL = RD->getLocation();
        SourceLocation SLE = RD->getLocEnd();

        std::string dummy = Rewrite.getRewrittenText(SourceRange(SL, SLE));
        Rewrite.ReplaceText(SourceRange(SL, SLE), StringRef(newname));
      }
    }

  private:
    Rewriter &Rewrite;
};
/**********************************************************************************************************************/
class PPInclusion : public PPCallbacks
{
public:
  explicit PPInclusion (SourceManager *SM, Rewriter *Rewrite) : SM(*SM), Rewrite(*Rewrite) {}

  virtual void MacroDefined(const Token &MacroNameTok, const MacroDirective *MD) {
    const MacroInfo* MI = MD->getMacroInfo();

    SourceLocation SL = MacroNameTok.getLocation(); 
    if (!SM.isInMainFile(SL)) return void();
    if (!SM.isWrittenInMainFile(SL)) return void();
    CheckSLValidity(SL);
    std::string macroname = MacroNameTok.getIdentifierInfo()->getName().str();
    std::size_t hash = std::hash<std::string>{}(macroname);
    std::string newname = "ID" + std::to_string(hash);
#ifdef DBG
    std::cout << "Macro name: " << macroname << " Hash: " << hash << " New ID: " << newname << "\n";
#endif

    //std::string dummy = Rewrite.getRewrittenText(SourceRange(MacroNameTok.getLocation(), MacroNameTok.getLocation().getLocWithOffset(MacroNameTok.getLength())));
    //std::cout << dummy << "\n";
    Rewrite.ReplaceText(SourceRange(MacroNameTok.getLocation(), MacroNameTok.getLocation().getLocWithOffset(MacroNameTok.getLength())), newname);
  }

private:
  const SourceManager &SM;
  Rewriter &Rewrite;
};
/**********************************************************************************************************************/
class BlankDiagConsumer : public clang::DiagnosticConsumer
{
  public:
    BlankDiagConsumer() = default;
    virtual ~BlankDiagConsumer() {}
    virtual void HandleDiagnostic(DiagnosticsEngine::Level DiagLevel, const Diagnostic &Info) override {}
};
/**********************************************************************************************************************/
class MyASTConsumer : public ASTConsumer {
public:
  MyASTConsumer(Rewriter &R) : funcDeclHandler(R), HandlerForVar(R), HandlerForClass(R), HandlerForCalledFunc(R), HandlerForCalledVar(R) {
    Matcher.addMatcher(functionDecl().bind("funcdecl"), &funcDeclHandler);
    Matcher.addMatcher(varDecl().bind("vardecl"), &HandlerForVar);
    Matcher.addMatcher(recordDecl(isClass()).bind("classdecl"), &HandlerForClass);
    //Matcher.addMatcher(callExpr().bind("calledfunc"), &HandlerForCalledFunc);
    Matcher.addMatcher(declRefExpr().bind("calledvar"), &HandlerForCalledVar);
  }

  void HandleTranslationUnit(ASTContext &Context) override {
    Matcher.matchAST(Context);
  }

private:
  FuncDecl funcDeclHandler;
  VDecl HandlerForVar;
  ClassDecl HandlerForClass;
  CalledFunc HandlerForCalledFunc;
  CalledVar HandlerForCalledVar;
  MatchFinder Matcher;
};
/**********************************************************************************************************************/
class ObfFrontendAction : public ASTFrontendAction {
public:
  ObfFrontendAction() {}
  ~ObfFrontendAction() {delete BDCProto;}
  void EndSourceFileAction() override {
    TheRewriter.getEditBuffer(TheRewriter.getSourceMgr().getMainFileID()).write(llvm::outs());
  }

  std::unique_ptr<ASTConsumer> CreateASTConsumer(CompilerInstance &CI, StringRef file) override {
    CI.getPreprocessor().addPPCallbacks(llvm::make_unique<PPInclusion>(&CI.getSourceManager(), &TheRewriter));
    DiagnosticsEngine &DE = CI.getPreprocessor().getDiagnostics();
    DE.setClient(BDCProto, false);
    TheRewriter.setSourceMgr(CI.getSourceManager(), CI.getLangOpts());
    return llvm::make_unique<MyASTConsumer>(TheRewriter);
  }

private:
  BlankDiagConsumer* BDCProto = new BlankDiagConsumer;
  Rewriter TheRewriter;
};
/**********************************************************************************************************************/
/*Main*/
int main(int argc, const char **argv) {
  CommonOptionsParser op(argc, argv, MatcherSampleCategory);
  ClangTool Tool(op.getCompilations(), op.getSourcePathList());
  return Tool.run(newFrontendActionFactory<ObfFrontendAction>().get());
}
/**********************************************************************************************************************/
/*last line intentionally left blank.*/

