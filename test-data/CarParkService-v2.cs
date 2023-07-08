using Ardalis.GuardClauses;
using AutoMapper;
using Domain.Dtos;
using Domain.Entities;
using Infrastructure.Authorisation;
using Infrastructure.Exceptions;
using Infrastructure.Persistence;
using Infrastructure.Services.DataContracts.UbiPark;
using Infrastructure.Util;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;

namespace Infrastructure.Services;

public class CarParkService : ICarParkService
{
    private readonly IUbiParkDataAccessService _ubiParkDataAccessService;
    private readonly UserIdentity _userIdentity;
    private readonly ApplicationDatabaseContext _dbContext;
    private readonly IGuidProvider _guidProvider;
    private readonly IMapper _mapper;
    private readonly ILogger<CarParkService> _logger;

    public CarParkService(
        UserIdentity userIdentity,
        ApplicationDatabaseContext dbContext,
        IUbiParkDataAccessService ubiParkDataAccessService,
        IMapper mapper,
        IGuidProvider guidProvider,
        ILogger<CarParkService> logger)
    {
        _ubiParkDataAccessService = ubiParkDataAccessService;
        _userIdentity = userIdentity;
        _dbContext = dbContext;
        _guidProvider = guidProvider;
        _mapper = mapper;
        _logger = logger;

    }

    public async Task<IList<CarParkProductDto>> GetProductsAsync(CarParkProductSearchRequestDto carParkSearchRequest, CancellationToken cancellationToken)
    {
        var availabilityRequest = new ProductAvailableRequest
        {
            EffectiveFrom = carParkSearchRequest.EntryFrom,
            EffectiveTo= carParkSearchRequest.ExitBy,
            PromoCode = carParkSearchRequest.PromoCode
        };
        _logger.LogInformation("Initiating car parking request for {carParkRequestEntryDate}", carParkSearchRequest.EntryFrom);

        var result = await _ubiParkDataAccessService.AvailableCarParkProductsList(availabilityRequest, cancellationToken);
        if (!result.Success || result.Products == null)
        {
            _logger.LogWarning("Car parking request did not return availability for {carParkRequestEntryDate}", carParkSearchRequest.EntryFrom);
            return new List<CarParkProductDto>();
        }
        var carProducts = result.Products.Where(p => p.Result).Select(cp => _mapper.Map<CarParkProductDto>(cp)).ToList();
        //re-populate promoCode value as currently response does not return sent in request promo code
        carProducts.ForEach(p => p.PromoCode = carParkSearchRequest.PromoCode!);
        return carProducts.ToList();
    }

    public async Task<CarParkUserDetails> ObtainUserAsync(CancellationToken cancellationToken)
    {
        var ubiParkUserId =
            (await _dbContext.CarParkUserInfo
            .SingleOrDefaultAsync(u => u.UserId == _userIdentity.UserId, cancellationToken))?
            .UbiparkUserId;

        // Create user if not exists
        if (string.IsNullOrEmpty(ubiParkUserId)) return await CreateUser(cancellationToken);

        // Get user if exists, Update user if information has changed and return
        var existingCarParkUser = await GetUser(ubiParkUserId, cancellationToken);
        if (UserInformationHasChanged(existingCarParkUser)) await UpdateUser(existingCarParkUser, cancellationToken);

        return existingCarParkUser;
    }

    private async Task<CarParkUserDetails> CreateUser(CancellationToken cancellationToken)
    {
        var request = new CreateUserRequest
        {
            UserID = _guidProvider.NewGuid.ToString(),
            Email = _userIdentity.Email,
            FirstName = _userIdentity.FirstName,
            LastName = _userIdentity.LastName,
            PhoneNo = _userIdentity.MobilePhone
        };

        _logger.LogInformation("Create user {UserId}", request.UserID);

        var result = await _ubiParkDataAccessService.CreateUser(request, cancellationToken);

        if (!result.Success)
        {
            var errors = string.Join(',', result.Errors);
            throw new CarParkServiceException($"Failed to create user {request.UserID}. Errors: {errors}");
        }

        _dbContext.CarParkUserInfo.Add(new CarParkUserInfo
        {
            UserId = _userIdentity.UserId,
            UbiparkUserId = result.UserID
        });

        await _dbContext.SaveChangesAsync(cancellationToken);

        return new CarParkUserDetails
        {
            UserId = result.UserID,
            Email = _userIdentity.Email,
            FirstName = _userIdentity.FirstName,
            LastName = _userIdentity.LastName,
            PhoneNo = _userIdentity.MobilePhone,
            CardToken = result.CardToken,
            PublishableKey = result.PublishableKey
        };
    }

    private async Task<CarParkUserDetails> GetUser(string ubiParkUserId, CancellationToken cancellationToken)
    {
        _logger.LogInformation("Get information about user {UserId}", ubiParkUserId);

        var result = await _ubiParkDataAccessService.GetUser(new UserRequest { UserID = ubiParkUserId }, cancellationToken);

        if (!result.Success)
        {
            var errors = string.Join(',', result.Errors);
            throw new CarParkServiceException($"Failed to get user {ubiParkUserId}. Errors: {errors}");
        }

        return new CarParkUserDetails
        {
            UserId = ubiParkUserId,
            Email = result.Email,
            FirstName = result.FirstName,
            LastName = result.LastName,
            PhoneNo = result.PhoneNo,
            CardToken = result.CardToken,
            PublishableKey = result.PublishableKey,
            HasCreditCard = result.HasCreditCard,
            PromisePayCardName = result.PromisePayCardName,
            CardType = result.CardType,
            ExpiryDate = result.ExpiryDate,
            CardNumber = result.CardNumber
        };
    }

    private async Task UpdateUser(CarParkUserDetails existingCarParkUser, CancellationToken cancellationToken)
    {
        Guard.Against.Null(existingCarParkUser);

        var updateUserRequest = new UpdateUserRequest
        {
            UserID = existingCarParkUser.UserId,
            Email = _userIdentity.Email,
            FirstName = _userIdentity.FirstName,
            LastName = _userIdentity.LastName,
            PhoneNo = _userIdentity.MobilePhone
        };

        var result = await _ubiParkDataAccessService.UpdateUser(updateUserRequest, cancellationToken);
        if (!result.Success)
        {
            var errors = string.Join(',', result.Errors);
            _logger.LogError("Failed to update user {UserId}. Errors: {Errors}", updateUserRequest.UserID, errors);
        }
        else
        {
            existingCarParkUser.Email = _userIdentity.Email;
            existingCarParkUser.FirstName = _userIdentity.FirstName;
            existingCarParkUser.LastName = _userIdentity.LastName;
            existingCarParkUser.PhoneNo = _userIdentity.MobilePhone;
        }
    }

    private bool UserInformationHasChanged(CarParkUserDetails existingCarParkUser)
    {
        Guard.Against.Null(existingCarParkUser);

        return existingCarParkUser.Email != _userIdentity.Email ||
            existingCarParkUser.FirstName != _userIdentity.FirstName ||
            existingCarParkUser.LastName != _userIdentity.LastName ||
            existingCarParkUser.PhoneNo != _userIdentity.MobilePhone;
    }
}