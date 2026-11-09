# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **Organization Owners & Event Managers:** Coordinate company-wide events, manage team rosters, assign role permissions (`Owner`, `Manager`, `Staff`), schedule shifts, and monitor real-time attendance readiness.
- **Event Staff & Team Members:** View upcoming personal shift assignments across multiple organizations, verify shift windows and venue locations, and confirm or update attendance status in one tap.

## Product Purpose

Eve is a multi-organization event and shift scheduling platform built on Django. It eliminates spreadsheet and messaging fragmentation by connecting company membership roles (`CompanyMember`), scheduled events (`Event`), and individual shift assignments (`EventAssignment`) into a single operational workspace.

## Positioning

A multi-workspace shift coordination platform where a single user account can belong to multiple organizations with distinct role permissions (`Owner`, `Manager`, `Staff`) and track live shift confirmation telemetry across all of them.

## Operating Context

- Used across desktop and mobile web browsers before and during live events.
- Supports both Daylight (`Light`) and low-ambient venue (`Pro Dark`) appearance modes via user preferences (`UserSettings.dark_mode`).

## Capabilities and Constraints

- **Authentication & Onboarding:** Email or username sign-in, account registration with automatic initial organization `Owner` provisioning, and instant one-tap demo account switching (`owner@demo.com`, `manager@demo.com`, `staff1@demo.com`).
- **Organization & Role Management:** Create organizations, discover and join existing workspaces as `Staff`, and promote/demote or remove members (`Owner` / `Manager` access control).
- **Event & Shift Lifecycle:** Full CRUD for events (`Upcoming`, `Draft`, `Completed`, `Cancelled`), member shift assignment with specific duties, stations, and time windows, and live attendance confirmation tracking (`Assigned`, `Confirmed`, `Completed`, `Cancelled`).

## Brand Commitments

- **Visual Reference:** Apple's official website (`apple.com`) and Apple Human Interface Guidelines—minimalist, spacious, typographic, and product-focused.
