package sprint

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"time"

	"github.com/chightow/canon-skills/internal/commands"
	"github.com/chightow/canon-skills/internal/parsers"
)

func GetSprintBoard(projectRoot string) map[string]any {
	ticketsDir := filepath.Join(projectRoot, ".tickets")
	tickets := parsers.ParseTickets(ticketsDir)
	handoff := parsers.ParseHandoff(filepath.Join(projectRoot, "HANDOFF.md"))

	var ticketList []map[string]any
	for _, t := range tickets {
		planPath := filepath.Join(ticketsDir, t.ID, "plan.md")
		ticketList = append(ticketList, map[string]any{
			"id":                  t.ID,
			"status":              t.Status,
			"title":               t.Title,
			"description":         t.Description,
			"priority":            t.Priority,
			"acceptance_criteria": t.AcceptanceCriteria,
			"plan_approved":       parsers.ParsePlanApproved(planPath),
			"plan_decision":       parsers.ParsePlanDecision(planPath),
		})
	}
	if ticketList == nil {
		ticketList = []map[string]any{}
	}

	return map[string]any{
		"tickets":      ticketList,
		"handoff":      handoff,
		"project_root": projectRoot,
	}
}

func LogSubagentRun(projectRoot, agentID, agentType, sessionID string) map[string]any {
	ts := time.Now().UTC().Format("2006-01-02T15:04:05Z")
	entry := map[string]any{
		"ts":              ts,
		"session_id":      sessionID,
		"agent_id":        agentID,
		"agent_type":      agentType,
		"transcript_path": "",
	}
	for _, rel := range parsers.AgentRunLogPaths {
		logFile := filepath.Join(projectRoot, rel)
		os.MkdirAll(filepath.Dir(logFile), 0755)
		f, err := os.OpenFile(logFile, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
		if err != nil {
			continue
		}
		json.NewEncoder(f).Encode(entry)
		f.Close()
	}
	return map[string]any{"status": "ok", "entry": entry}
}

func StartSprint(projectRoot, title, ticketID, priority string) map[string]any {
	ticketsDir := filepath.Join(projectRoot, ".tickets")

	var tid string
	if ticketID != "" {
		tdir := filepath.Join(ticketsDir, ticketID)
		if _, err := os.Stat(tdir); os.IsNotExist(err) {
			return map[string]any{"error": fmt.Sprintf("Ticket '%s' not found", ticketID)}
		}
		tid = ticketID
	} else {
		result := commands.CreateSprintTicket(ticketsDir, title, priority)
		if err, ok := result["error"]; ok {
			return map[string]any{"error": err}
		}
		tid = result["ticket_id"].(string)
	}

	tdir := filepath.Join(ticketsDir, tid)
	planFile := filepath.Join(tdir, "plan.md")
	if _, err := os.Stat(planFile); os.IsNotExist(err) {
		os.WriteFile(planFile, []byte(
			fmt.Sprintf("---\nid: %s\n---\n\n# Plan\n\nTicket: `%s`\n\n## Sign-off\n\n- [ ] Plan approved — proceed to implementation\n\n## Approach\n\n\n## Files\n\n\n## Decisions\n\n", tid, tid),
		), 0644)
	}

	for _, pair := range [][2]string{
		{filepath.Join(projectRoot, "DECISIONS.md"), "# Decisions\n\n| Date | Decision | Reason |\n|---|---|---|\n"},
		{filepath.Join(projectRoot, "HANDOFF.md"), "# Handoff\n\n## Current Focus\n\n## In Progress\n\n## Discoveries\n\n## Next Steps\n\n1. \n"},
	} {
		if _, err := os.Stat(pair[0]); os.IsNotExist(err) {
			os.WriteFile(pair[0], []byte(pair[1]), 0644)
		}
	}

	os.WriteFile(filepath.Join(ticketsDir, "ACTIVE"), []byte(tid+"\n"), 0644)

	return map[string]any{
		"ticket_id":   tid,
		"ticket_dir":  tdir,
		"status":      "ok",
		"message":     fmt.Sprintf("Sprint started: %s", tid),
	}
}

func CloseSprint(projectRoot string) map[string]any {
	ticketsDir := filepath.Join(projectRoot, ".tickets")
	handoffPath := filepath.Join(projectRoot, "HANDOFF.md")

	terminalStatuses := map[string]bool{"closed": true, "cancelled": true, "archived": true}
	tickets := parsers.ParseTickets(ticketsDir)

	if len(tickets) == 0 {
		return map[string]any{"status": "error", "message": "No tickets found. Nothing to close."}
	}

	var incomplete []string
	for _, t := range tickets {
		if !terminalStatuses[strings.ToLower(t.Status)] {
			incomplete = append(incomplete, t.ID)
		}
	}
	if len(incomplete) > 0 {
		return map[string]any{
			"status":  "error",
			"message": fmt.Sprintf("Cannot close sprint. The following tickets are not terminal (closed/cancelled/archived): %s", strings.Join(incomplete, ", ")),
		}
	}

	trivialRe := regexp.MustCompile(`(?i)tier\s*:?\s*\*{0,2}trivial`)
	verdictPassRe := regexp.MustCompile(`(?m)^pass:`)

	for _, t := range tickets {
		if strings.ToLower(t.Status) != "closed" {
			continue
		}
		tdir := filepath.Join(ticketsDir, t.ID)
		planPath := filepath.Join(tdir, "plan.md")
		reportPath := filepath.Join(tdir, "eval-report.md")

		if planContent, err := os.ReadFile(planPath); err == nil {
			if trivialRe.Match(planContent) {
				continue
			}
		}

		reportContent, err := os.ReadFile(reportPath)
		if err != nil {
			return map[string]any{
				"status":  "error",
				"message": fmt.Sprintf("Ticket %s cannot close: eval-report.md is missing. Run the evaluator (eval skill) before closing, or confirm trivial tier in plan.md.", t.ID),
			}
		}

		runIDRe := regexp.MustCompile(`(?m)^evaluator-run-id:\s+(\S+)`)
		runIDMatch := runIDRe.FindStringSubmatch(string(reportContent))
		if runIDMatch == nil {
			return map[string]any{
				"status":  "error",
				"message": fmt.Sprintf("Ticket %s cannot close: eval-report.md is missing evaluator-run-id field. Ensure the evaluator subagent wrote the run-id before grading.", t.ID),
			}
		}

		runID := runIDMatch[1]
		runParts := strings.SplitN(runID, "-", 2)
		runEpochStr := ""
		if len(runParts) > 0 {
			runEpochStr = runParts[0]
		}
		if runEpochStr != "" {
			var runEpoch int64
			if _, err := fmt.Sscanf(runEpochStr, "%d", &runEpoch); err == nil {
				matched := parsers.CheckSubagentRun(projectRoot, runEpoch)
				if !matched {
					return map[string]any{
						"status":  "error",
						"message": fmt.Sprintf("Ticket %s cannot close: evaluator-run-id '%s' has no matching subagent entry in .canon/.claude/.opencode subagent-runs.jsonl (±60 min window). The eval must be run as a real subagent invocation — inline writes are not accepted.", t.ID, runID),
					}
				}
			}
		}

		if !verdictPassRe.Match(reportContent) {
			verdictLine := "(no verdict line found)"
			if m := regexp.MustCompile(`(?m)^(pass|fail):`).FindString(string(reportContent)); m != "" {
				verdictLine = m
			}
			return map[string]any{
				"status":  "error",
				"message": fmt.Sprintf("Ticket %s cannot close: eval-report.md verdict is not pass. %s", t.ID, verdictLine),
			}
		}
	}

	var receiptLines []string
	receiptLines = append(receiptLines, "## Delivery Receipt", "| Ticket ID | Status | Title |", "| --- | --- | --- |")
	for _, t := range tickets {
		receiptLines = append(receiptLines, fmt.Sprintf("| %s | %s | %s |", t.ID, t.Status, t.Title))
	}
	receiptContent := strings.Join(receiptLines, "\n")

	handoffBytes, err := os.ReadFile(handoffPath)
	if err != nil {
		return map[string]any{"status": "error", "message": "HANDOFF.md not found"}
	}
	handoffContent := string(handoffBytes)

	sprintID := tickets[0].ID
	summaryHeading := fmt.Sprintf("## Sprint Summary (%s)", sprintID)
	if strings.Contains(handoffContent, summaryHeading) {
		return map[string]any{
			"status":  "error",
			"message": fmt.Sprintf("Sprint %s already has a summary in HANDOFF.md. Remove the existing section first if you need to re-close.", sprintID),
		}
	}

	summarySection := fmt.Sprintf("\n\n%s\n%s\n", summaryHeading, receiptContent)
	newHandoff := strings.TrimRight(handoffContent, " \t\r\n") + summarySection
	os.WriteFile(handoffPath, []byte(newHandoff), 0644)

	return map[string]any{
		"status":  "ok",
		"message": "Sprint closed successfully and HANDOFF.md updated.",
		"receipt": receiptContent,
	}
}
