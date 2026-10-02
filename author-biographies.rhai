let meta = #{
    name: "author-biographies",
    description: "Research a Hebrew biography for every author in the seforim database",
    phases: [
        #{ title: "Research", detail: "One researcher per batch of four authors" },
        #{ title: "Index", detail: "Rebuild the Hebrew index from the files on disk" },
    ],
};

let root = "/Users/elie/seforim-author-biographies";
let total = 96;
if args != () && args.total != () {
    total = args.total;
}

phase("Research");
let jobs = [];
let n = 0;
while n < total {
    n += 1;
    let num = n.to_string();
    if n < 10 {
        num = "00" + num;
    } else if n < 100 {
        num = "0" + num;
    }
    let b = root + "/data/batches/batch-" + num + ".json";
    let prompt = "";
    prompt += "You are writing Hebrew biographies of rabbinic authors from a seforim database. ";
    prompt += "Read and follow every rule in " + root + "/INSTRUCTIONS.md before you write anything. ";
    prompt += "Read the tone sample at " + root + "/authors/0165.md once. Do not copy its facts onto other people. ";
    prompt += "Your batch file is " + b + ". Read that JSON. ";
    prompt += "For each author, use web_search and then open_page on at least one reliable page before writing. ";
    prompt += "Memory is not a source, including for famous rabbis. ";
    prompt += "Write one markdown file per author to " + root + "/authors/<id padded to 4 digits>.md exactly as the instructions specify. ";
    prompt += "Skip an author when that file already exists and contains a markdown heading. ";
    prompt += "Do not invent dates, places, teachers, or books. If sources are insufficient, write an honest short stub. ";
    prompt += "When you finish, reply with only the JSON object the instructions require.";
    jobs.push(#{
        prompt: prompt,
        label: "batch-" + n.to_string(),
        capability_mode: "all",
    });
}
let results = parallel(jobs);

phase("Index");
let index_prompt = "";
index_prompt += "Run exactly this command and do not edit any biography file: ";
index_prompt += "python3 " + root + "/build_index.py";
index_prompt += " Then report the command output.";
let index = agent(index_prompt, #{ label: "index", capability_mode: "execute" });

let ok = 0;
let bad = 0;
for r in results {
    if r != () && r.success {
        ok += 1;
    } else {
        bad += 1;
    }
}
let index_ok = false;
if index != () && index.success {
    index_ok = true;
}
complete(#{
    batches_ok: ok,
    batches_failed: bad,
    index_success: index_ok,
});
