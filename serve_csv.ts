// import fs and read the csv
import { readFileSync } from "fs";

Bun.serve({
    port: 8080,
    fetch(req) {
        const csv = readFileSync("boxoffice/db/data/movies.csv", "utf-8");
        return new Response(csv, {
            headers: {
                "content-type": "text/csv",
                "Access-Control-Allow-Origin": "*",
            },
        });
    },
});

console.log("Bun is served!");
