// import csv parse from d3
import { csvParse } from "d3-dsv";

export async function load({ fetch }) {
    // fetch from current url /csv
    const fetched = await fetch("/csv");

    return {
        data: csvParse(await fetched.text())
    }
}
