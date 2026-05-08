# Schema

The canonical schema is defined in [`src/hotline_helper/models.py`](../src/hotline_helper/models.py) using Pydantic. This document is a friendlier reference.

## Top-level: `CountryFile`

Every file under `data/countries/{ISO}.yml` matches this shape.

```yaml
country: <Country>
emergency_services: [<EmergencyService>, ...]   # may be empty
hotlines: [<Hotline>, ...]                       # may be empty
metadata: <Metadata>
```

### `Country`

| Field | Type | Notes |
| ----- | ---- | ----- |
| `iso_code` | string (2 chars) | ISO 3166-1 alpha-2, uppercase. |
| `iso3` | string (3 chars) | Optional, ISO 3166-1 alpha-3. |
| `name` | string | English country name. |
| `region` | string | UN region (Europe / Asia / Africa / Americas / Oceania / Antarctica). |
| `subregion` | string | Optional. |

### `EmergencyService`

Generic emergency line, separate from crisis hotlines.

| Field | Type | Notes |
| ----- | ---- | ----- |
| `name` | string | "Emergency Services", "Police", "SAMU", etc. |
| `phone` | string | Dialable as-shown. |
| `notes` | string | Optional. |

### `Hotline`

| Field | Type | Notes |
| ----- | ---- | ----- |
| `id` | slug | Lowercase-hyphenated, must be unique within country. e.g. `us-988`. |
| `name` | string | Official hotline name. Don't auto-translate; preserve as-listed. |
| `aliases` | list of strings | Optional. Other names by which it's commonly known. |
| `categories` | list of `Category` | Required, ≥1. |
| `contacts` | `Contacts` | Required, ≥1 channel. |
| `languages` | list of strings | ISO 639-1 codes (`en`, `es`, ...). |
| `hours` | `Hours` | When the line is reachable. |
| `cost` | `Cost` | `free` / `paid` / `varies` / `unknown`. |
| `fees_note` | string | Optional. e.g. "Free; SMS rates may apply." |
| `target_population` | string | Free-text, e.g. `"youth"`, `"veterans"`. |
| `operator` | `OperatorType` | `government` / `ngo_government_funded` / `ngo` / `private`. |
| `operator_name` | string | Who actually runs the line. |
| `notes` | string | Free-text supplementary info. |
| `source` | `Source` | Required. Where this entry came from. |

### `Contacts`

At least one of `phone`, `phone_alt`, `sms`, `chat_url`, `email`, `website` must be set.

| Field | Type | Notes |
| ----- | ---- | ----- |
| `phone` | string | Primary number, formatted as listed. |
| `phone_alt` | string | Optional secondary (mobile, WhatsApp). |
| `sms` | string | SMS shortcode. |
| `chat_url` | URL | Online chat. |
| `email` | string | |
| `website` | URL | |

### `Hours`

```yaml
hours:
  type: 24/7    # 24/7 | business_hours | evening | weekends_only | custom | unknown
  details: ...  # required when type is custom; optional context otherwise
```

### `Source`

| Field | Type | Notes |
| ----- | ---- | ----- |
| `name` | string | Human-readable, e.g. "SAMHSA" or "NHS England". |
| `url` | URL | Required. |
| `type` | string | `government` / `intergovernmental` / `academic` / `ngo`. |
| `last_verified` | date (YYYY-MM-DD) | When a maintainer or scraper last confirmed this entry against the source. |

### `Metadata`

```yaml
metadata:
  last_updated: 2026-05-08            # required
  last_scraped: 2026-05-08            # optional
  verification_status: verified        # verified | unverified | no_government_source
  data_sources:                        # array of URLs
    - https://...
  notes: ...                           # optional
```

## `Category` enum values

`suicide`, `mental_health`, `crisis`, `domestic_violence`, `sexual_assault`, `child_abuse`, `youth`, `lgbtq`, `substance_abuse`, `elder_abuse`, `veterans`, `general_emergency`, `discrimination`.

## `OperatorType` enum values

`government`, `ngo_government_funded`, `ngo`, `private`, `unknown`.

## Example

See [`data/countries/US.yml`](../data/countries/US.yml) and [`data/countries/FR.yml`](../data/countries/FR.yml) for two full, verified examples.

## API response shapes

The runtime API and the static JSON tree both serialize using `CountryFile.model_dump(mode="json")`. The shape matches this schema 1:1, except for the listing endpoints (`/v1/countries`, `/v1/categories`) which return summaries. See [`src/hotline_helper/api.py`](../src/hotline_helper/api.py) for the exact responses.
