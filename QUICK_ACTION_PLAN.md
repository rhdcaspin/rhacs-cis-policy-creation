# Quick Action Plan: Integrating into StackRox
## Immediate Next Steps (This Week)

This is your **action-oriented** guide to start the journey of integrating compliance reporting into StackRox/RHACS.

---

## 🎯 Goal

Transform your standalone compliance reporting tool into a native StackRox/RHACS feature.

---

## 📅 Week 1: Setup & Research (Days 1-7)

### Day 1: Environment Setup

```bash
# 1. Clone StackRox repository
cd ~/Projects
git clone https://github.com/stackrox/stackrox.git
cd stackrox

# 2. Read the main README
cat README.md

# 3. Check development setup docs
ls docs/
cat docs/development.md  # or similar
```

**Install Prerequisites:**
```bash
# Based on StackRox requirements (typically):
brew install go@1.21
brew install node@18
brew install yarn
brew install docker
brew install kind  # Kubernetes in Docker
```

**Verify Setup:**
```bash
go version    # Should be 1.21+
node --version  # Should be 18+
yarn --version
docker --version
```

### Day 2: Explore the Codebase

**Key Directories to Understand:**
```bash
cd ~/Projects/stackrox

# Backend (Go)
ls central/            # Main central services
ls pkg/                # Shared packages
ls proto/              # API definitions

# Frontend (React)
ls ui/                 # User interface

# Look for compliance-related code
find . -name "*compliance*" -type d
grep -r "compliance" --include="*.go" | head -20

# Look for report-related code
find . -name "*report*" -type d
grep -r "report" --include="*.go" | head -20
```

**Read Key Files:**
```bash
# Architecture
cat docs/ARCHITECTURE.md  # or similar

# API structure
ls proto/api/v1/
cat proto/api/v1/compliance_service.proto  # if exists

# Compliance implementation
ls central/compliance/
```

### Day 3: Join the Community

**1. Join StackRox Slack**
- Go to: https://stackrox.slack.com
- Introduce yourself in #general
- Join #contributors channel
- Join #dev-discussions channel

**2. Review Open Issues**
```bash
# Search for compliance-related issues
https://github.com/stackrox/stackrox/issues?q=is%3Aissue+compliance

# Search for reporting features
https://github.com/stackrox/stackrox/issues?q=is%3Aissue+report
```

**3. Check the Roadmap**
- Look for existing compliance initiatives
- Identify potential overlaps
- Find alignment opportunities

### Day 4: Study RHACS API

**Understand Current API:**
```bash
# Look at your existing integration
cd ~/Projects/claude/compliance_reporting

# Review how you're using the API
cat nist_compliance_reporting/nist_compliance_report.py

# Document the endpoints you use
echo "Current API usage:" > api_analysis.md
grep "api_request" nist_compliance_reporting/*.py >> api_analysis.md
```

**API Endpoints You Use:**
- `/v1/policies` - Policy retrieval
- `/v1/alerts` - Violation data
- `/v1/deployments` - Deployment information

**Map to StackRox Code:**
```bash
cd ~/Projects/stackrox

# Find policy service
find . -path "*/central/policy/*" -name "*.go"

# Find alert service
find . -path "*/central/alert/*" -name "*.go"

# Find deployment service
find . -path "*/central/deployment/*" -name "*.go"
```

### Day 5: Create Feature Proposal

**Draft GitHub Issue:**

Create a file: `feature_proposal_draft.md`

```markdown
# Feature Proposal: NIST 800-190 Compliance Reporting Dashboard

## Summary
Add native NIST 800-190 compliance reporting to RHACS with dashboard,
export capabilities, and automated report generation.

## Problem Statement
Organizations struggle to demonstrate NIST 800-190 compliance across
their container deployments. Currently:
- Manual policy review is time-consuming
- No unified compliance view across clusters
- Difficult to generate audit-ready reports
- No trending or historical compliance data

## Current Workaround
I've built a proof-of-concept using the RHACS API that demonstrates
the value: [link to your GitHub repo]

**PoC Capabilities:**
- Scans 520 deployments across 91 namespaces
- Checks 12 NIST 800-190 policies
- Generates reports in JSON, CSV, and HTML
- Red Hat branded dashboards

**User Feedback:**
[Add any feedback you've received]

## Proposed Solution

### Core Features
1. **Compliance Dashboard**
   - Overview statistics (compliant/non-compliant deployments)
   - Policy-by-policy compliance breakdown
   - Drill-down: Cluster → Namespace → Deployment

2. **Report Export**
   - JSON (API integration)
   - CSV (spreadsheet analysis)
   - PDF (audit documentation)

3. **Scheduled Reports**
   - Daily/weekly/monthly automation
   - Email notifications
   - Webhook integrations

4. **Compliance Trending**
   - Historical compliance data
   - Improvement tracking
   - Executive dashboards

### Technical Approach
- Backend: Go service in `central/compliance/nist80190/`
- API: gRPC/REST endpoints
- Frontend: React components in compliance section
- Database: PostgreSQL for historical data

### Benefits
- **Time Savings**: Reduce compliance reporting from days to minutes
- **Audit Ready**: Generate audit-ready reports on demand
- **Visibility**: Real-time compliance posture across all clusters
- **Trending**: Track compliance improvements over time

## Implementation Plan
1. Phase 1: Core reporting (4 weeks)
2. Phase 2: UI integration (3 weeks)
3. Phase 3: Automation (3 weeks)
4. Phase 4: Production hardening (2 weeks)

## Resources
- PoC Repository: [your repo]
- Live Demo: [demo video if available]
- Related Issues: [link to related issues]

## Questions for Maintainers
1. Is this feature aligned with the product roadmap?
2. Are there existing compliance initiatives I should coordinate with?
3. What's the preferred contribution approach (single PR vs incremental)?
4. Any architectural concerns or suggestions?

## Next Steps
- Gather community feedback
- Refine technical design
- Create development plan
- Submit initial PR with data models
```

### Day 6-7: Build Development Plan

**Create Technical Design Doc:**

File: `technical_design.md`

```markdown
# NIST 800-190 Compliance Reporting - Technical Design

## Architecture

### Backend Components

#### 1. Compliance Service
**Location**: `central/compliance/nist80190/`

**Structure**:
```
central/compliance/nist80190/
├── service.go                 # Main service implementation
├── generator.go              # Report generation logic
├── datastore/
│   ├── datastore.go         # Data access layer
│   └── postgres.go          # PostgreSQL implementation
├── aggregator.go            # Policy violation aggregation
└── types.go                 # Data models
```

**Key Types**:
```go
type ComplianceReport struct {
    ClusterCompliance map[string]*ClusterCompliance
    Summary          *ComplianceSummary
    GeneratedAt      time.Time
}

type ClusterCompliance struct {
    ClusterID   string
    ClusterName string
    Namespaces  map[string]*NamespaceCompliance
}

type NamespaceCompliance struct {
    Namespace   string
    Deployments map[string]*DeploymentCompliance
}

type DeploymentCompliance struct {
    DeploymentID    string
    DeploymentName  string
    PolicyResults   map[string]*PolicyResult
    OverallStatus   ComplianceStatus
}
```

#### 2. API Endpoints
**Location**: `proto/api/v1/compliance_service.proto`

```protobuf
service ComplianceService {
  rpc GetNIST800190Report(ComplianceReportRequest)
      returns (ComplianceReport);

  rpc ExportNIST800190Report(ExportRequest)
      returns (stream ExportChunk);

  rpc ScheduleNIST800190Report(ScheduleRequest)
      returns (ScheduleResponse);
}
```

#### 3. Database Schema
**Tables**:
- `compliance_reports` - Cached report data
- `compliance_schedules` - Scheduled report configs
- `compliance_history` - Historical compliance snapshots

### Frontend Components

#### 1. Routes
```typescript
/main/compliance/nist-800-190
/main/compliance/nist-800-190/reports
/main/compliance/nist-800-190/schedule
```

#### 2. Component Structure
```
ui/apps/platform/src/Containers/Compliance/NIST80190/
├── Dashboard/
│   ├── index.tsx
│   ├── OverviewCards.tsx
│   ├── PolicyComplianceChart.tsx
│   └── DeploymentTable.tsx
├── Export/
│   └── ExportDialog.tsx
├── Schedule/
│   └── ScheduleConfig.tsx
└── hooks/
    ├── useComplianceReport.ts
    └── useExport.ts
```

## Data Flow

1. **Report Generation**:
   ```
   User Request → API Gateway → ComplianceService
                                      ↓
   PolicyStore ← ← ← ← ← ← ← ← ← ComplianceGenerator
   AlertStore  ← ← ← ← ← ← ← ← ← ←      ↓
   DeploymentStore ← ← ← ← ← ← ← ←      ↓
                                         ↓
   ComplianceDataStore → → → → → Cache Report
                                         ↓
   API Response ← ← ← ← ← ← ← ← ← ← ← Return
   ```

2. **Frontend Rendering**:
   ```
   React Component → useComplianceReport hook
                              ↓
   API Call → /v1/compliance/nist-800-190/report
                              ↓
   Process Response → Update State
                              ↓
   Re-render Components
   ```

## Implementation Phases

### Phase 1: Backend Foundation (Week 1-2)
- [ ] Create compliance service structure
- [ ] Implement data models
- [ ] Add basic report generation
- [ ] Write unit tests

### Phase 2: API Layer (Week 3)
- [ ] Define protobuf messages
- [ ] Implement gRPC service
- [ ] Add REST endpoints
- [ ] Integration tests

### Phase 3: Frontend (Week 4-5)
- [ ] Create dashboard route
- [ ] Build overview components
- [ ] Add data fetching
- [ ] Implement export functionality

### Phase 4: Advanced Features (Week 6-7)
- [ ] Scheduled reports
- [ ] Historical data
- [ ] PDF generation
- [ ] Email notifications

### Phase 5: Production (Week 8)
- [ ] Performance optimization
- [ ] Security review
- [ ] Documentation
- [ ] Release preparation

## Testing Strategy

### Unit Tests
- Go: `*_test.go` files with >80% coverage
- React: Jest + React Testing Library

### Integration Tests
- API endpoint tests
- Database integration tests
- E2E UI tests with Cypress

### Performance Tests
- Load test with 10,000+ deployments
- Report generation time <30s
- API response time <2s p95

## Security Considerations

- RBAC: Respect existing cluster/namespace permissions
- Audit: Log all report generations
- Data Privacy: No PII in compliance reports
- Export Security: Sign/encrypt exported reports

## Rollout Plan

1. **Alpha** (Internal testing)
   - Feature flag: `compliance-nist-800-190-alpha`
   - Limited to dev/staging environments

2. **Beta** (Early adopters)
   - Feature flag: `compliance-nist-800-190-beta`
   - Opt-in for selected customers

3. **GA** (General availability)
   - Feature flag: `compliance-nist-800-190-ga`
   - Full release

## Documentation

- User Guide: How to use compliance dashboard
- API Documentation: API reference
- Developer Guide: Contributing to the feature
- Admin Guide: Configuration and tuning
```

---

## 🚀 Week 2: Create & Share Proposal

### Action Items

**Monday:**
- [ ] Finalize feature proposal
- [ ] Create demo video of your PoC
- [ ] Prepare before/after comparison

**Tuesday:**
- [ ] Create GitHub Discussion (not Issue yet)
- [ ] Post in StackRox Slack #contributors
- [ ] Share demo video

**Wednesday:**
- [ ] Respond to initial feedback
- [ ] Refine proposal based on comments
- [ ] Identify potential blockers

**Thursday-Friday:**
- [ ] Connect with interested maintainers
- [ ] Schedule sync meeting if needed
- [ ] Document next steps

---

## 📧 Communication Templates

### Slack Introduction

```
Hi everyone! 👋

I'm [Your Name], and I've been working with RHACS for compliance automation.

I've built a PoC for NIST 800-190 compliance reporting that:
- Scans 500+ deployments against 12 NIST policies
- Generates JSON/CSV/HTML reports
- Provides executive-ready dashboards

I'd love to contribute this as a native RHACS feature. I've created a
proposal in GitHub Discussions: [link]

Demo video: [link]
Code: https://github.com/rhdcaspin/rhacs-cis-policy-creation

Looking forward to feedback and collaboration!
```

### GitHub Discussion Template

```markdown
# 💡 Feature Discussion: NIST 800-190 Compliance Reporting

Hi maintainers and community!

I'd like to propose adding NIST 800-190 compliance reporting as a
native feature in RHACS.

## Background
[Your background and why this matters]

## Proof of Concept
I've built a working PoC that demonstrates the concept:
- Repository: [link]
- Demo: [video link]
- Live report: [screenshot]

## Proposed Integration
[High-level architecture]

## Questions
1. Does this align with the roadmap?
2. Are there similar initiatives in progress?
3. What's the best way to contribute this?

Looking forward to your feedback!
```

---

## 🛠️ Development Setup Checklist

Once you get the green light to proceed:

**StackRox Development Environment:**
```bash
# 1. Fork the repository
# Go to https://github.com/stackrox/stackrox
# Click "Fork"

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/stackrox.git
cd stackrox

# 3. Add upstream remote
git remote add upstream https://github.com/stackrox/stackrox.git

# 4. Create feature branch
git checkout -b feature/nist-800-190-compliance

# 5. Build the project
make  # or follow docs/development.md

# 6. Run tests
make test

# 7. Start local development
make dev-up  # or similar command
```

**Your Development Workflow:**
```bash
# Work in your feature branch
git checkout feature/nist-800-190-compliance

# Make changes
# ... code ...

# Run tests
make test

# Format code
make fmt

# Lint
make lint

# Commit with good messages
git commit -m "feat(compliance): Add NIST 800-190 data models"

# Push to your fork
git push origin feature/nist-800-190-compliance

# Create PR from your fork to stackrox/stackrox
```

---

## 📊 Success Criteria

### Week 1
- [ ] StackRox repo cloned and buildable
- [ ] Joined Slack and introduced yourself
- [ ] Reviewed existing compliance code
- [ ] Created feature proposal draft

### Week 2
- [ ] Feature proposal posted (Discussion)
- [ ] Received initial feedback from maintainers
- [ ] Demo video shared
- [ ] Development plan drafted

### Week 3-4
- [ ] Approval to proceed (or pivot based on feedback)
- [ ] First PR submitted (data models)
- [ ] Code review engaged
- [ ] Tests passing

---

## 🤝 Getting Help

**If you get stuck:**

1. **Slack**: Ask in #contributors or #dev-discussions
2. **GitHub**: Comment on your Discussion
3. **Office Hours**: Join community meetings
4. **Code Review**: Tag maintainers for review
5. **Documentation**: Read docs/ thoroughly

**Common Questions:**

Q: How long does code review take?
A: Typically 1-3 days for small PRs, longer for large changes

Q: Who should I tag for review?
A: Check CODEOWNERS file or ask in Slack

Q: My PR has merge conflicts, what do I do?
A: Rebase on latest main, resolve conflicts

---

## 🎯 Key Takeaways

1. **Start with Community** - Don't code in isolation
2. **Small Increments** - Submit small, focused PRs
3. **Be Patient** - Open source takes time
4. **Show Value** - Demo the benefit clearly
5. **Collaborate** - Work with maintainers, not around them

---

## 📅 Calendar Reminder

Set these reminders:

- **Day 1**: Clone StackRox, read docs
- **Day 3**: Join Slack, introduce yourself
- **Day 5**: Post feature proposal
- **Day 7**: Review feedback, adjust plan
- **Day 14**: Submit first PR (if approved)

---

## 🎬 Next Action

**Right now, do this:**

```bash
# 1. Clone StackRox
cd ~/Projects
git clone https://github.com/stackrox/stackrox.git

# 2. Read the README
cd stackrox
cat README.md

# 3. Join Slack
# Go to: https://stackrox.slack.com
```

**Then:**
Draft your feature proposal and share it!

Good luck! 🚀
