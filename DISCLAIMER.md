# Disclaimer

**Please read this in full before integrating Hotline Helper into a product, especially a healthcare product.**

## Not a substitute for emergency services

Hotline Helper is a public dataset of crisis and suicide-prevention hotlines compiled from government sources. It is **not** an emergency dispatch service, a clinical triage tool, or a substitute for the judgment of a qualified clinician.

If a user is in immediate danger, the right action is to direct them to **local emergency services** (e.g., 911 in the US, 112 in the EU, 000 in Australia). Hotline numbers can be busy, rerouted, or no longer in service.

## Best-effort, not authoritative

Although every entry cites a government source, the dataset is:

- **Eventually consistent.** Data is refreshed monthly via an automated scraper; numbers can change between refreshes.
- **Not exhaustive.** Many countries have regional or specialty hotlines we do not list.
- **Not always reachable.** A hotline being listed by a government does not guarantee 24/7 availability, language coverage as listed, or current operational status.
- **Subject to scraper error.** Automated extraction can introduce mistakes (wrong number, transposed digits, wrong language tag). Maintainer review reduces but does not eliminate these.

## How to integrate responsibly

If you are a healthcare or telehealth company integrating this data:

1. **Show the source.** Display the `source.url` and `last_verified` date alongside each hotline. Users in crisis benefit from knowing the data has a provenance.
2. **Provide multiple options.** Show emergency services first (e.g., 911/112), then the hotline list. Don't make a hotline number the only path forward.
3. **Verify before launch.** Spot-check every number you display in your product against the cited source before going live.
4. **Re-verify periodically.** Pull fresh data at least monthly. Consider an internal alert if a number has changed.
5. **Localize and translate carefully.** Hotline names are often proper nouns; do not auto-translate them. Language codes in the dataset are best-effort.
6. **Have a fallback.** If your network call to this dataset fails, ship a hardcoded set of internationally-recognized fallbacks (e.g., IASP, Befrienders Worldwide).
7. **Get clinical review.** Have a qualified clinician on your team review the integration end-to-end.

## No warranty

Per the [MIT license](LICENSE) (code) and [CC0 dedication](DATA_LICENSE) (data), this project is provided "as is" with no warranty of any kind. The maintainers and contributors disclaim all liability arising from use, misuse, or unavailability of the dataset.

## Reporting incorrect data

If you find a number that is wrong, out of date, or rerouted, please [open a data correction issue](.github/ISSUE_TEMPLATE/data_correction.yml). Include the cited source so a maintainer can verify and update.

If you cannot wait for a maintainer review and the data is actively dangerous (e.g., a number is now reaching the wrong service), email the maintainers directly via the address listed in `pyproject.toml`.
