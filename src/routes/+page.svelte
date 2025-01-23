<script lang="ts">
  import Main from "../components/Main.svelte";
  import { Toast, Button, Helper } from "flowbite-svelte";
  import { onMount, tick } from "svelte";
  import {
    CheckCircleSolid,
    CloseCircleSolid,
    TrashBinSolid,
    UploadSolid,
  } from "flowbite-svelte-icons";
  import QuotationInputModal from "../components/QuotationInputModal.svelte";
  import { Fileupload, Label } from "flowbite-svelte";
  import { testQuotationInput, type QuotationInput } from "$lib/types";

  let financialAuditFiles: (FileList | undefined | null)[] = [undefined];
  let proposalFormFile: FileList | undefined = undefined;

  $: if (financialAuditFiles[financialAuditFiles.length - 1]) {
    financialAuditFiles = [...financialAuditFiles, undefined];
  }

  // let quotationInput: QuotationInput | null = testQuotationInput;
  let quotationInput: QuotationInput | null = null;
  let isLoading = false;
  let toastIsError = false;
  let toastText = "";
  let toastShowTimeout: NodeJS.Timeout | null = null;
  const defaultHometext = "Welcome to the AI Underwriter";
  let homeText = defaultHometext;

  function showToast(text: string, isError = false, duration_ms = 4000) {
    if (toastShowTimeout) {
      clearTimeout(toastShowTimeout);
    }
    toastText = text;
    toastShowTimeout = setTimeout(() => {
      toastText = "";
    }, duration_ms);
    toastIsError = isError;
  }

  let homeTextLoadingInterval: NodeJS.Timeout | null = null;
  let currentPeriodCount = 1;
  let maxPeriodCount = 3;
  let homeTextLoading = "";

  function updateHometextLoading() {
    if (currentPeriodCount > maxPeriodCount) {
      currentPeriodCount = 0;
    }
    homeTextLoading = `${".".repeat(currentPeriodCount)}`;
    currentPeriodCount++;
  }

  function showLoading(task: string) {
    isLoading = true;
    homeText = task;
    if (homeTextLoadingInterval) {
      clearInterval(homeTextLoadingInterval);
    }
    homeTextLoadingInterval = setInterval(() => {
      updateHometextLoading();
    }, 200);
  }

  function resetLoading() {
    isLoading = false;
    if (homeTextLoadingInterval) {
      clearInterval(homeTextLoadingInterval);
    }
    homeTextLoading = "";
    homeText = defaultHometext;
  }

  async function getQuotationInput(
    proposalForm: File,
    financialAudits: File[]
  ) {
    console.log("Extracting proposal info.. .");
    showLoading("Processing");
    showToast("This may take a while...", false);
    const formData = new FormData();
    formData.append("proposalForm", proposalForm);
    financialAudits.forEach((f) => formData.append("financialAudit", f));
    let success = false;

    try {
      const resp = await fetch("/quotation/input", {
        method: "POST",
        body: formData,
      });
      success = resp.ok;
      if (success) {
        const resp_json = await resp.json();
        quotationInput = resp_json.data.quotation_input;
        console.log("Extracted!");
      }
    } catch (error) {
      console.log("Error extracting");
      console.error(error);
    }
    resetLoading();
    if (!success) {
      resetLoading();
      showToast("Failed to extract proposal info", true);
      return;
    }
  }

  async function validateAndUpload() {
    const financialAudits = financialAuditFiles
      .filter((f) => f !== null && f !== undefined)
      .map((f) => f[0]);
    if (!proposalFormFile && !financialAudits) {
      showToast("Please add both files", true);
      return;
    }
    if (!proposalFormFile) {
      showToast("Please add a proposal form", true);
      return;
    }
    if (!financialAudits.length) {
      showToast("Please add a financial audit", true);
      return;
    }
    const proposalForm = proposalFormFile[0];
    if (
      !proposalForm.name.endsWith(".pdf") ||
      financialAudits.some((f) => !f.name.endsWith(".pdf"))
    ) {
      showToast("All files must be in PDF format", true);
      return;
    }
    await getQuotationInput(proposalForm, financialAudits);
  }

  onMount(() => {
    titleStyle = { transform: "translateX(0)", opacity: 1 };
  });
  let titleStyle = { transform: "translateX(-200px)", opacity: 0 };
</script>

<Main {isLoading}>
  {#if toastText}
    <Toast
      class="absolute top-0 right-0 toast"
      on:close={() => (toastText = "")}
      color={toastIsError ? "red" : "green"}
    >
      <svelte:fragment slot="icon">
        {#if toastIsError}
          <CloseCircleSolid class="w-5 h-5" />
        {:else}
          <CheckCircleSolid class="w-5 h-5" />
        {/if}
      </svelte:fragment>
      {toastText}
    </Toast>
  {/if}
  {#if quotationInput}
    <QuotationInputModal
      {quotationInput}
      {showToast}
      {showLoading}
      {resetLoading}
      open={!!quotationInput}
    />
  {/if}
  <div
    class="z-10 justify-center items-center h-screen flex flex-col space-y-20"
  >
    <h1
      class="z-10 title"
      style="transform: {titleStyle.transform}; opacity: {titleStyle.opacity};"
    >
      {homeText}
      <span class="">
        {homeTextLoading}
      </span>
    </h1>
    <div class="z-10 flex flex-col gap-6 items-center">
      <div class="z-10 flex gap-10">
        <div class="space-y-2">
          <Label>Financial audits and accounts</Label>

          {#each financialAuditFiles as file}
            {#if file !== null}
              <div class="flex gap-2 items-baseline">
                <Fileupload
                  type="file"
                  class="hover:cursor-pointer"
                  bind:files={file}
                />
                {#if file}
                  <Button
                    size="sm"
                    on:click={(e) => {
                      file = null;
                    }}
                  >
                    <TrashBinSolid size="sm" />
                  </Button>
                {/if}
              </div>
            {/if}
          {/each}
        </div>
        <div class="space-y-2">
          <Label>PI Proposal form</Label>
          <Fileupload
            class="hover:cursor-pointer"
            bind:files={proposalFormFile}
          />
        </div>
      </div>
      <Button
        class="flex gap-2 w-min hover:scale-110 ease-in-out duration-300"
        on:click={validateAndUpload}
      >
        <div>Upload</div>
        <UploadSolid />
      </Button>
    </div>
    <div />
  </div></Main
>

<style>
  .title {
    font-size: 3rem;
    font-weight: bold;
    transition:
      transform 4s,
      opacity 4s;
  }
</style>
