package models

type Ticket struct {
	ID                 string `json:"id"`
	Status             string `json:"status"`
	Title              string `json:"title"`
	Description        string `json:"description,omitempty"`
	Priority           string `json:"priority,omitempty"`
	AcceptanceCriteria string `json:"acceptance_criteria,omitempty"`
}

type PlanInfo struct {
	Approved bool   `json:"approved"`
	Decision string `json:"decision"`
}

type TicketResult struct {
	TicketID string            `json:"ticket_id"`
	Files    map[string]string `json:"files,omitempty"`
	Plan     PlanInfo          `json:"plan"`
}

type Handoff struct {
	ActiveTasks []string `json:"active_tasks"`
	Context     string   `json:"context"`
}

type SprintBoard struct {
	Tickets     []any  `json:"tickets"`
	Handoff     Handoff `json:"handoff"`
	ProjectRoot string `json:"project_root"`
}
