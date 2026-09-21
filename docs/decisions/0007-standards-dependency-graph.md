# 0007. Standards Dependency Graph & Compliance Intelligence Architecture

Date: 2026-09-21  
Status: Accepted  
Deciders: NORMVAULT Engineering Core  

## Context

Phase 4 successfully solved the problem of identifying primary and alternative applicable Indian Standards for procurement specifications with rigorous negative evidence prioritization. However, an Indian Standard does not operate in isolation:
1. Base product standards cite companion standards for test methods, safety requirements, dimensions, and codes of practice.
2. In standards literature, circular references are ubiquitous (e.g. equipment standards cite test standards, which in turn cite equipment ratings and tolerances). Naive recursive graph traversal risks infinite recursion or memory exhaustion.
3. In procurement tenders, engineers frequently conflate *"referenced in standard"* with *"mandatory for bidding"*. This leads to tender disputes and inflated vendor pricing.
4. Furthermore, technical applicability is distinct from statutory licensing mandates: an equipment standard may apply technically, yet the product may not fall under an active Quality Control Order (QCO) notified under the Bureau of Indian Standards Act, 2016.

## Decision

1. **Typed Directed Reference Graph with Explicit Cycle Suppression**:
   Model standards cross-citations as a directed graph. Enforce a strict traversal depth limit (`max_depth = 3`). Maintain active DFS path history to detect circular loops (`is_cycle = True`), log the cyclic chain diagnostic, and immediately halt recursion along that branch.

2. **Strict Direct vs. Transitive Separation**:
   Explicitly partition graph references into **Depth 1 Direct References** (immediate companion standards invoked by the citing clause) and **Depth $\ge 2$ Transitive References** (standards cited by the companion standards). Never conflate these tiers in APIs or UI presentations.

3. **Multi-State Reference Semantics & Procurement Impact**:
   Tag every reference edge with four semantic states (`NORMATIVE`, `INFORMATIVE`, `CONDITIONAL`, `UNKNOWN`) and map them to concrete procurement impacts (`REQUIRED_SPECIFICATION`, `REQUIRED_TEST`, `REQUIRED_SAFETY_CONDITION`, `REQUIRED_INSTALLATION_CONDITION`, `INFORMATIONAL`, `CONDITIONAL`, `UNKNOWN`).

4. **Decoupling Technical Applicability from Statutory QCO Mandates**:
   Maintain distinct domain entities for `IndianStandard` applicability and `CertificationRequirement`. A standard is marked `is_mandatory_qco = True` ONLY when backed by an indexed Gazette Order issued by a competent Central Ministry.

5. **Principled Uncertainty on Regulatory Currentness**:
   If a QCO record cannot be verified against the latest Gazette notification or BIS S.O. update, mark its currentness status as `CURRENTNESS_UNCERTAIN` and alert the procurement officer, rather than presenting unverified claims as settled law.

6. **Resilience to Unindexed Reference Targets**:
   When a referenced standard is not in the indexed database (e.g. international IEC/ISO standards or pending BIS additions), instantiate a placeholder `DependencyNode` with `is_indexed = False`. Never crash, discard the edge, or hallucinate missing clauses.

## Consequences

- **Positive**:
  - Full visibility into the complete standard ecosystem (tests, safety, installation, allied products) for procurement planning.
  - Zero risk of infinite recursion or stack overflow on cyclic citations.
  - Transparent legal boundaries preventing false claims of mandatory QCO enforcement.
  - Ultra-fast traversal latencies ($< 5\text{ ms}$) suitable for interactive UI workflows.
- **Negative**:
  - Requires continuous ingestion of referenced standards to maximize graph traversal depth and eliminate unindexed terminal nodes.
  - Regulatory QCO data requires synchronization with Gazette of India publications to avoid `CURRENTNESS_UNCERTAIN` warnings.
