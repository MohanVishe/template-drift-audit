// tda-render renders chat prompts with Ollama's own template and renderer code,
// pinned by go.mod to the Ollama version under study. It reads one JSON request
// per line on stdin and writes one JSON response per line on stdout. No network,
// no model weights, no server.
//
//	{"op":"render","source":"go_template","template":"...","messages":[...],"tools":[...],"think":true}
//	{"op":"render","source":"renderer","renderer":"qwen3.5","messages":[...]}
//	{"op":"inspect","template":"..."}   -> identifiers and inferred thinking tags
//	{"op":"version"}
package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"os"
	"runtime/debug"

	"github.com/ollama/ollama/api"
	"github.com/ollama/ollama/model/renderers"
	"github.com/ollama/ollama/template"
	"github.com/ollama/ollama/thinking"
)

type request struct {
	Op       string          `json:"op"`
	Source   string          `json:"source"`
	Template string          `json:"template"`
	Renderer string          `json:"renderer"`
	Messages []api.Message   `json:"messages"`
	Tools    []api.Tool      `json:"tools"`
	Think    *api.ThinkValue `json:"think"`
}

type response struct {
	OK         bool      `json:"ok"`
	Error      string    `json:"error,omitempty"`
	Prompt     *string   `json:"prompt,omitempty"`
	LeadingBOS string    `json:"leading_bos,omitempty"`
	Vars       []string  `json:"vars,omitempty"`
	ThinkTags  *[2]string `json:"think_tags,omitempty"`
	Ollama     string    `json:"ollama,omitempty"`
}

func ollamaVersion() string {
	if info, ok := debug.ReadBuildInfo(); ok {
		for _, dep := range info.Deps {
			if dep.Path == "github.com/ollama/ollama" {
				return dep.Version
			}
		}
	}
	return "unknown"
}

// render mirrors server.renderPrompt (server/prompt.go) for one source.
func render(req request) response {
	switch req.Source {
	case "renderer":
		p, err := renderers.RenderWithRenderer(req.Renderer, req.Messages, req.Tools, req.Think)
		if err != nil {
			return response{Error: err.Error()}
		}
		return response{OK: true, Prompt: &p, LeadingBOS: renderers.LeadingBOSForRenderer(req.Renderer)}
	case "go_template":
		t, err := template.Parse(req.Template)
		if err != nil {
			return response{Error: "parse: " + err.Error()}
		}
		thinkVal, thinkLevel := false, ""
		if req.Think != nil {
			thinkVal, thinkLevel = req.Think.Bool(), req.Think.String()
		}
		var b bytes.Buffer
		v := template.Values{Messages: req.Messages, Tools: req.Tools, Think: thinkVal, ThinkLevel: thinkLevel, IsThinkSet: req.Think != nil}
		if err := t.Execute(&b, v); err != nil {
			return response{Error: "execute: " + err.Error()}
		}
		p := b.String()
		return response{OK: true, Prompt: &p}
	}
	return response{Error: fmt.Sprintf("unknown source %q", req.Source)}
}

func inspect(req request) response {
	t, err := template.Parse(req.Template)
	if err != nil {
		return response{Error: "parse: " + err.Error()}
	}
	vars, err := t.Vars()
	if err != nil {
		return response{Error: "vars: " + err.Error()}
	}
	open, close := thinking.InferTags(t.Template)
	return response{OK: true, Vars: vars, ThinkTags: &[2]string{open, close}}
}

func main() {
	in := bufio.NewScanner(os.Stdin)
	in.Buffer(make([]byte, 0, 1<<20), 64<<20)
	out := json.NewEncoder(os.Stdout)
	out.SetEscapeHTML(false)
	for in.Scan() {
		var req request
		var resp response
		if err := json.Unmarshal(in.Bytes(), &req); err != nil {
			resp = response{Error: "bad request: " + err.Error()}
		} else {
			switch req.Op {
			case "render":
				resp = render(req)
			case "inspect":
				resp = inspect(req)
			case "version":
				resp = response{OK: true, Ollama: ollamaVersion()}
			default:
				resp = response{Error: fmt.Sprintf("unknown op %q", req.Op)}
			}
		}
		if err := out.Encode(resp); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
	}
	if err := in.Err(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
