<script lang="ts">
  import { Label, Input, Button, Toggle, Modal } from "flowbite-svelte";
  import { quotationOutput } from "$lib/store";
  import {
    ClipboardListSolid,
    BadgeCheckSolid,
    CloseCircleSolid,
    UsersGroupSolid,
    BriefcaseSolid,
    CalendarMonthSolid,
    CashSolid,
    ProfileCardOutline,
    UploadOutline,
  } from "flowbite-svelte-icons";
  import { testQuotationInput, type QuotationInput } from "$lib/types";
  import { goto } from "$app/navigation";
  import { API_BASE_URL } from "$lib/consts";
  export let quotationInput: QuotationInput = testQuotationInput
  export let open: boolean;
  export let showToast: (text: string, isError?: boolean) => void;
  export let showLoading: (task: string) => void;
  export let resetLoading: () => void;
  let showFinancialSummary = !quotationInput.is_profitable;
  function convertQuotationInputToProperFormat(quotationInput: QuotationInput) {
    return {
      reinsured_name: quotationInput.reinsured_name,
      broker_name: quotationInput.broker_name,
      insured_name: quotationInput.insured_name,
      // @ts-ignore
      partners_count: parseInt(quotationInput.partners_count),
      qualified_assistants_count: parseInt(
        // @ts-ignore
        quotationInput.qualified_assistants_count
      ),
      unqualified_assistants_count: parseInt(
        // @ts-ignore
        quotationInput.unqualified_assistants_count
      ),
      // @ts-ignore
      others_count: parseInt(quotationInput.others_count),
      // @ts-ignore
      annual_fees: parseFloat(quotationInput.annual_fees),
      // @ts-ignore
      limit_of_indemnity: parseFloat(quotationInput.limit_of_indemnity),
      profession: quotationInput.profession,
      loss_of_documents: quotationInput.loss_of_documents,
      libel_and_slander: quotationInput.libel_and_slander,
      dishonest_employees: quotationInput.dishonest_employees,
      retroactive_cover: quotationInput.retroactive_cover,
    };
  }
  async function generateQuotation() {
    open = false;
    showLoading("Generating quotation");
    console.log("Generating quotation...");
    
    const properQuotationInput = convertQuotationInputToProperFormat(quotationInput);
    let success = false;
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
      
      const resp = await fetch(`/quotation/output`, {
        method: "POST",
        body: JSON.stringify({ quotation_input: properQuotationInput }),
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Origin': '*'
        },
        signal: controller.signal,
        credentials: 'omit'
      });
      
      clearTimeout(timeoutId);
      success = resp.ok;
      
      if (success) {
        const resp_json = await resp.json();
        $quotationOutput = resp_json.data.quotation_output;
        console.log("Quotation generated successfully");
      } else {
        throw new Error(`HTTP error! status: ${resp.status}`);
      }
    } catch (error) {
      console.error("Fetch error:", error);
      showToast(`Failed to generate quotation: ${(error as Error).message}`, true);
      resetLoading();
      return;
    }

    if (success) {
      goto("/quotation/output/");
    }
    resetLoading();
  }
</script>

<Modal
  title={showFinancialSummary ? "Financial Summary" : "Quotation Input"}
  size="lg"
  bind:open
  autoclose={false}
>
  {#if showFinancialSummary}
    <div class="z-0 flex flex-col m-auto mt-2 justify-center items-center p-4">
      <slot name="header">
        <div class="flex gap-2 items-center">
          {#if quotationInput.is_profitable}
            <BadgeCheckSolid size="md" color="green" />
            <Label class="text-green-500 text-base"
              >The organisation is profitable</Label
            >
          {:else}
            <CloseCircleSolid size="md" color="red" />
            <Label class="text-red-500 text-base"
              >The organization is not profitable</Label
            >
          {/if}
        </div>
      </slot>
      <p class="p-4">{quotationInput.financial_summary}</p>
      <slot name="footer">
        <div class="items-center flex">
          <Button
            class="hover:scale-110 duration-300 ease-in-out"
            color="green"
            on:click={() => (showFinancialSummary = false)}
          >
            <div class="flex items-center gap-2">
              <p>Quotation input</p>
              <ClipboardListSolid />
            </div>
          </Button>
        </div>
      </slot>
    </div>
  {:else}
    <div class="z-0 flex flex-col m-auto mt-2 justify-center items-center">
      <div class=" flex-col p-2 mb-5 grid gap-10 border rounded-lg">
        <div class="flex gap-5 justify-between">
          <div class="pb-1 flex flex-col">
            <div class="flex items-center">
              <ProfileCardOutline />
              <Label class="pl-2" for="reinsured_name">Reinsured</Label>
            </div>
            <Input
              id="reinsured_name"
              bind:value={quotationInput.reinsured_name}
            />
          </div>
          <div class="pb-1">
            <div class="flex items-center">
              <ProfileCardOutline />
              <Label class="pl-2" for="broker_name">Broker</Label>
            </div>
            <Input id="broker_name" bind:value={quotationInput.broker_name} />
          </div>
          <div class="pb-1">
            <div class="flex items-center">
              <ProfileCardOutline />
              <Label class="pl-2" for="insured_name">Insured</Label>
            </div>
            <Input id="insured_name" bind:value={quotationInput.insured_name} />
          </div>
        </div>
        <div class="flex gap-5 justify-between">
          <div>
            <div class="pb-1 flex items-center">
              <UsersGroupSolid />
              <Label class="pl-2" for="partners_count">Partners</Label>
            </div>
            <Input
              id="partners_count"
              type="number"
              bind:value={quotationInput.partners_count}
            />
          </div>
          <div>
            <div class="pb-1 flex items-center">
              <UsersGroupSolid />
              <Label class="pl-2" for="qualified_assistants_count"
                >Qualified assistants</Label
              >
            </div>
            <Input
              id="qualified_assistants_count"
              bind:value={quotationInput.qualified_assistants_count}
              type="number"
              placeholder="Qualified Assistants Count"
            />
          </div>
          <div>
            <div class="pb-1 flex items-center">
              <UsersGroupSolid />
              <Label class="pl-2" for="unqualified_assistants_count"
                >Unqualified assistants</Label
              >
            </div>
            <Input
              id="unqualified_assistants_count"
              type="number"
              bind:value={quotationInput.unqualified_assistants_count}
              placeholder="Unqualified Assistants Count"
            />
          </div>
          <div>
            <div class="pb-1 flex items-center">
              <UsersGroupSolid />
              <Label class="pl-2" for="others_count">Other employees</Label>
            </div>
            <Input
              id="others_count"
              type="number"
              bind:value={quotationInput.others_count}
              placeholder="Others Count"
            />
          </div>
        </div>
        <div class="flex gap-4 justify-between">
          <div>
            <div class="flex pb-1">
              <CalendarMonthSolid />
              <Label class="pl-2">Annual fees</Label>
            </div>

            <Input
              id="annual_fees"
              type="number"
              bind:value={quotationInput.annual_fees}
              placeholder="Annual Fees"
            />
          </div>
          <div class="">
            <div class="flex pb-1">
              <CashSolid />
              <Label class="pl-2" for="limit_of_indemnity"
                >Limit of indemnity</Label
              >
            </div>
            <Input
              id="limit_of_indemnity"
              type="number"
              bind:value={quotationInput.limit_of_indemnity}
              placeholder="Limit of Indemnity"
            />
          </div>
          <div>
            <div class="flex items-center pb-1">
              <BriefcaseSolid />
              <Label class="pl-2" for="profession">Profession</Label>
            </div>
            <Input
              id="profession"
              bind:value={quotationInput.profession}
              placeholder="Profession"
            />
          </div>
        </div>
        <div class="flex gap-5 justify-between">
          <div class="pb-1 items-center flex flex-col">
            <Label>Loss of documents</Label>
            <Toggle
              class="hover:cursor-pointer"
              bind:checked={quotationInput.loss_of_documents}
            />
          </div>
          <div class="pb-1 items-center flex flex-col">
            <Label>Libel and slander</Label>
            <Toggle
              class="hover:cursor-pointer"
              bind:checked={quotationInput.libel_and_slander}
            />
          </div>
          <div class="pb-1 items-center flex flex-col">
            <Label>Dishonest employees</Label>
            <Toggle
              class="hover:cursor-pointer"
              bind:checked={quotationInput.dishonest_employees}
            />
          </div>

          <div class="pb-1 items-center flex flex-col">
            <Label>Retroactive cover</Label>
            <Toggle
              class="hover:cursor-pointer"
              bind:checked={quotationInput.retroactive_cover}
            />
          </div>
        </div>
      </div>
      <slot name="footer">
        <div class="flex gap-4">
          <Button
            on:click={generateQuotation}
            class="hover:scale-110 duration-300 ease-in-out"
          >
            <div class="flex items-center gap-2">
              <p>Generate quotation</p>
              <UploadOutline />
            </div>
          </Button>
          <Button
            class="hover:scale-110 duration-300 ease-in-out"
            color="green"
            on:click={() => (showFinancialSummary = true)}
          >
            <div class="flex items-center gap-2">
              <p>Financial summary</p>
              <CashSolid />
            </div>
          </Button>
        </div>
      </slot>
      <div />
    </div>
  {/if}
</Modal>

<style>
</style>
